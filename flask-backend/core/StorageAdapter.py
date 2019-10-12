from core.TelegramMessageWrapper import TelegramMessageWrapper
from core.CallbackData import CallbackData
from typing import Optional, Dict, Any, Union
from credentials.credentials import POSTGRE_USER_PASSWORD
from sqlalchemy import create_engine
from sqlalchemy import Column, String, Integer, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uuid
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()
engine = create_engine(
    f'postgres+psycopg2://postgres:{POSTGRE_USER_PASSWORD}@35.246.160.33:5432/main'
)


class UserSchema(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    prefered_name = Column(String, nullable=True)
    user_name = Column(String, nullable=True)
    birthdate = Column(Date, nullable=True)

    def __repr__(self):
        return '; '.join(map(lambda attribute: f"{attribute}={self.__getattribute__(attribute)}",
                             filter(lambda s: not s.startswith('_'), self.__dir__())))


class RandomCoffeeParticipantSchema(Base):
    __tablename__ = 'rc_participant'
    user_id = Column(Integer, primary_key=True)
    current_group_id = Column(Integer, nullable=True)
    meeting_frequency = Column(Integer, nullable=False)
    do_not_group_until = Column(Date, nullable=False)

    def __repr__(self):
        return '; '.join(map(lambda attribute: f"{attribute}={self.__getattribute__(attribute)}",
                             filter(lambda s: not s.startswith('_'), self.__dir__())))


class RandomCoffeeGroupSchema(Base):
    __tablename__ = 'rc_groups'
    group_id = Column(Integer, primary_key=True)
    created = Column(Date, nullable=False)
    deadline = Column(Date, nullable=False)

    def __repr__(self):
        return '; '.join(map(lambda attribute: f"{attribute}={self.__getattribute__(attribute)}",
                             filter(lambda s: not s.startswith('_'), self.__dir__())))


class MessageLogSchema(Base):
    __tablename__ = 'message_log'
    user_id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, primary_key=True)
    message_text = Column(String, nullable=False)

    def __repr__(self):
        return '; '.join(map(lambda attribute: f"{attribute}={self.__getattribute__(attribute)}",
                             filter(lambda s: not s.startswith('_'), self.__dir__())))


engine.table_names()
Base.metadata.create_all(engine)


class StorageAdapter:

    def __init__(self) -> None:
        self._user_dict: Dict[str, Any] = {}
        self._user_id_to_private_chat_id: Dict[str, str] = {}
        self._chats: Dict[str, str] = {}
        self._callback_payloads: Dict[str, Dict] = {}

    def add_user(self, user_id: str, user_info: Any) -> None:
        """ Adds user to the storage """
        self._user_dict[user_id] = user_info

    def add_chat(self,
                 chat_id: str,
                 private: bool,
                 user_id: Optional[str] = None,
                 purpose: Optional[str] = None) -> None:
        """ Adds chat_id to storage. If private is true, user_id have to be not None (otherwise method does nothing)"""
        if private is True and user_id is not None:
            self._user_id_to_private_chat_id[user_id] = chat_id
        elif private is False:
            self._chats[chat_id] = purpose

    def get_private_chat_id(self, user_id: str) -> Optional[str]:
        """ Returns a private chat id for given user id (if known. Returns None if unknown) """

        if user_id is not None:
            return self._user_id_to_private_chat_id.get(user_id)

    def add_callback_payload(self, payload: Dict[str, Union[str, Any]]) -> Optional[str]:
        """ Stores payload and returns uuid associated with it.
            Data can be retrieved by id with get_callback_payload method
            Payload must be a dict with at least one field called ca
        """
        if 'callback_id' not in payload:
            logger.warning(f"Attempted to save callback payload without callback_id. Payload: {payload}")
        payload_id = str(uuid.uuid4())
        self._callback_payloads[payload_id] = payload
        return payload_id

    def get_callback_payload(self, payload_id: str) -> Optional[Dict[str, Union[str, Any]]]:
        """ Retrieves previously stored with add_callback_payload payload by payload_id
        (returns None if no data was found) """
        return self._callback_payloads.get(payload_id)

    def get_first_introduction_message(self,
                                       chat_id: str,
                                       private: bool,
                                       user_first_name: Optional[str] = None) -> TelegramMessageWrapper:
        """ This is a job for storage adapter cause ultimately this message should be configurable on runtime """
        msg = ""

        if private is True:
            msg += f"Hi, {user_first_name}!\n" if user_first_name is not None else "Hi!\n"
            msg += f"As you can see from the name, i am a secretary for UpGrade community.\n"
            msg += f"Currently i can only help you with Random Coffee game " \
                   f"(but you need to talk to me in the chat that wants to play)\n\n"
            msg += f"I would love to learn to do more things! If you have an idea of what i should learn next, " \
                   f"describe it here: https://github.com/Nikita6000/upgrade-telegram-bot/issues"
            tg_msg = TelegramMessageWrapper(msg_text=msg)
        else:
            msg += f"Hi everyone!\n"
            msg += f"As you can see from the name, i am a secretary for UpGrade community.\n"
            msg += f"Currently i can only help you with Random Coffee game. If you want to play in this chat, " \
                   f"press button below\n\n"
            msg += f"I would love to learn to do more things! If you have an idea of what i should learn next, " \
                   f"describe it here: https://github.com/Nikita6000/upgrade-telegram-bot/issues"

            payload = {
                'callback_id': CallbackData.NewRandomCoffeeGame,
                'chat_id': chat_id
            }

            payload_id = self.add_callback_payload(payload)

            tg_msg = TelegramMessageWrapper(msg_text=msg, inline_reply_markup=[[("Play Random Coffee", payload_id)]])
        return tg_msg
