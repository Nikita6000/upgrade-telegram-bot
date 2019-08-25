from core.TelegramMessageWrapper import TelegramMessageWrapper
from core.TelegramPresenter import TelegramPresenter
from core.StorageAdapter import StorageAdapter
from typing import Optional


class User:
    """ A wrapper with basic info about user"""
    def __init__(self,
                 user_id: str,
                 first_name: str,
                 last_name: Optional[str],
                 username: Optional[str],
                 storage_adapter: StorageAdapter,
                 private_chat_id: Optional[str] = None):

        self.id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.private_chat_id = private_chat_id
        self._storage_adapter = storage_adapter

    def send_private_message(self, message: TelegramMessageWrapper, telegram_presenter: TelegramPresenter):
        """ If private_chat_id is known, sends private message according to the user settings """

        # TODO: make time of the private messages configurable

        self.private_chat_id = self._storage_adapter.get_private_chat_id(self.id)

        if self.private_chat_id is not None:
            telegram_presenter.send_message(chat_id=self.private_chat_id, message=message)

    def get_name_as_tg_mention(self, parse_mode: Optional[str] = None) -> str:
        """
            Returns string with users' first name as mention. If parse_mode is not specified, returns
            mention as @username. If parse mode and username is None, return just first name without mention
        """
        if parse_mode == TelegramMessageWrapper.parse_modes.Markdown:
            return f'[{self.first_name}](tg://user?id={self.id})'
        elif parse_mode == TelegramMessageWrapper.parse_modes.HTML:
            return f'<a href="tg://user?id={self.id}">{self.first_name}</a>'
        elif self.username is not None:
            return f'@{self.username}'
        else:
            return self.first_name
