import telegram
from credentials.telegram import BOT_TOKEN
from typing import Tuple, Optional, List
from utils.RandomCoffeeParticipant import RandomCoffeeParticipant
import logging

logger = logging.getLogger(__name__)


class TelegramPresenter:
    def __init__(self):
        self._bot = telegram.Bot(token=BOT_TOKEN)

    def send_message(self,
                     chat_id: str,
                     text: str,
                     parse_mode: Optional[str] = None,
                     reply_markup_constr: Optional[List[List[Tuple[str, str]]]] = None) -> None:
        if chat_id is None:
            logger.warn(f"Skipping attempt to send to chat_id=None message: {text}")
            return

        logger.info(f"Sending to chat_id: {chat_id} msg: {text}")
        reply_markup = None
        if reply_markup_constr is not None:
            reply_markup = telegram.InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            telegram.InlineKeyboardButton(
                                text=text,
                                callback_data=callback_data
                            )
                            for text, callback_data in button_list
                        ]
                        for button_list in reply_markup_constr
                    ]
                )

        self._bot.sendMessage(
            chat_id=chat_id,
            text=text,
            parse_mode=parse_mode,
            reply_markup=reply_markup
        )

    @staticmethod
    def get_name_as_mention(participant: RandomCoffeeParticipant) -> str:
        # if participant.user_name is not None:
        #     return f"@{participant.user_name}"
        # else:
        return f"[{participant.first_name}](tg://user?id={participant.id})"


