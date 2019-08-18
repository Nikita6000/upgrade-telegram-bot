from flask import request
from flask_restful import Resource
import logging
import telegram
from credentials.telegram import BOT_TOKEN
import json

logger = logging.getLogger(__name__)


class TelegramWebHook(Resource):
    def __init__(self):
        self._bot = telegram.Bot(token=BOT_TOKEN)

    def post(self):
        request_data = request.get_json(force=True)
        logger.info(request_data)
        update = telegram.Update.de_json(request_data, self._bot)
        logger.info(f"Chat id: {update.message.chat_id}, Msg id: {update.message.message_id}")
        logger.info(f"Text: {update.message.text}")

        self._bot.sendMessage(
            chat_id=update.message.chat_id,
            text=json.dumps(request_data, indent=4, sort_keys=True),
            reply_to_message_id=update.message.message_id
        )
        return 'done'
