from flask import request
from flask_restful import Resource
import logging
import telegram
from credentials.telegram import BOT_TOKEN
from utils.RandomCoffeeManager import RandomCoffeeManager

logger = logging.getLogger(__name__)


class TelegramWebHook(Resource):
    def __init__(self, rc_manager: RandomCoffeeManager):
        self._bot = telegram.Bot(token=BOT_TOKEN)
        self._rc_manager = rc_manager

    def post(self):
        request_data = request.get_json(force=True)
        logger.info(request_data)
        update = telegram.Update.de_json(request_data, self._bot)

        self._rc_manager.new_telegram_update(update)

        return None
