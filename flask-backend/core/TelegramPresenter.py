import telegram
from typing import Tuple, Optional, List
from core.User import User
from core.TelegramMessageWrapper import TelegramMessageWrapper

import logging

logger = logging.getLogger(__name__)


class TelegramPresenter:
    def __init__(self, bot: telegram.Bot):
        self._bot = bot

    def send_message(self,
                     chat_id: str,
                     message: TelegramMessageWrapper) -> None:
        if chat_id is None:
            logger.warn(f"Skipping attempt to send to chat_id=None message: {message.text}")
            return

        logger.info(f"Sending to chat_id: {chat_id} msg: {message.text}")

        self._bot.sendMessage(
            chat_id=chat_id,
            text=message.text,
            parse_mode=message.parse_mode,
            reply_markup=message.reply_markup
        )

    @staticmethod
    def get_name_as_mention(user: User, parse_mode: Optional[str] = None) -> str:
        """
            Returns string with users' first name as mention. If parse_mode is not specified, returns
            mention as @username. If parse mode and username is None, return just first name without mention
        """
        if parse_mode == 'Markdown':
            return f'[{user.first_name}](tg://user?id={user.id})'
        elif parse_mode == 'HTML':
            return f'<a href="tg://user?id={user.id}">{user.first_name}</a>'
        elif user.username is not None:
            return f'@{user.username}'
        else:
            return user.first_name



