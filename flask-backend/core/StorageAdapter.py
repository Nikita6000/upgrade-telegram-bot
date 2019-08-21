from core.User import User
from core.TelegramMessageWrapper import TelegramMessageWrapper
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class StorageAdapter:

    def __init__(self) -> None:
        self._user_dict: Dict[str, User] = {}
        self._user_id_to_private_chat_id: Dict[str, str] = {}
        self._chats: Dict[str, str] = {}

    def add_user(self, user: User) -> None:
        """ Adds user to the storage """
        logger.info(f"New user (name: {user.first_name}, username: {user.username}) added to the database")
        self._user_dict[user.id] = user

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

    @staticmethod
    def get_first_introduction_message() -> TelegramMessageWrapper:
        """ This is a job for storage adapter cause ultimately this message should be configurable on runtime """
        # TODO: create an introductory message
        return TelegramMessageWrapper(msg_text="")
