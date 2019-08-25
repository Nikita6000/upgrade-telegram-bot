import telegram
from typing import Optional, Union, List


class ParseModes:
    Markdown = 'Markdown'
    HTML = "HTMl"


class TelegramMessageWrapper:
    """ Wrapper around messages sent to telegram. """
    parse_modes = ParseModes()

    def __init__(self,
                 msg_text: str,
                 parse_mode: Optional[str] = None,
                 inline_reply_markup: Optional[List[List]] = None):

        self.text = msg_text
        self.parse_mode = parse_mode
        self._inline_reply_markup = inline_reply_markup

    @property
    def reply_markup(self) -> Optional[Union[telegram.InlineKeyboardMarkup,
                                             telegram.ReplyKeyboardMarkup,
                                             telegram.ReplyKeyboardRemove,
                                             telegram.ForceReply]]:
        if self._inline_reply_markup is not None:
            return telegram.InlineKeyboardMarkup(inline_keyboard=[
                    [
                        telegram.InlineKeyboardButton(
                            text=text,
                            callback_data=callback_data
                        )
                        for text, callback_data in button_list
                    ]
                    for button_list in self._inline_reply_markup
                ]
            )
        else:
            return None
