from core.TelegramMessageWrapper import TelegramMessageWrapper
from core.CallbackData import CallbackData
from typing import Optional, Dict, Any, Union
import uuid
import logging

logger = logging.getLogger(__name__)


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
