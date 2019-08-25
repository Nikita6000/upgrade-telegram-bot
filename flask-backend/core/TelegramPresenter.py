import telegram
from typing import Tuple, Optional, List
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
