import telegram
from credentials.telegram import BOT_TOKEN
from core.StorageAdapter import StorageAdapter
from core.TelegramPresenter import TelegramPresenter
from core.CallbackData import CallbackData
from core.User import User
from random_coffee.RandomCoffeeManager import RandomCoffeeManager
from random_coffee.RandomCoffeeStorageAdapter import RandomCoffeeStorageAdapter
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class RequestHandler:

    def __init__(self,
                 storage_adapter: Optional[StorageAdapter] = None,
                 tg_presenter: Optional[TelegramPresenter] = None,
                 rc_manager: Optional[RandomCoffeeManager] = None):
        # objects for communication with telegram
        self._bot = telegram.Bot(token=BOT_TOKEN)
        self._tg_presenter = tg_presenter if tg_presenter is not None else TelegramPresenter(self._bot)

        # storage
        self._storage_adapter = storage_adapter if storage_adapter is not None else StorageAdapter()

        # feature managers
        self._rc_manager = rc_manager if rc_manager is not None else RandomCoffeeManager(
            storage_adapter=RandomCoffeeStorageAdapter(),
            telegram_presenter=self._tg_presenter
        )

        self.introduced = False

    def new_request(self, json_request):

        update = telegram.Update.de_json(json_request, self._bot)

        if update.callback_query is not None:
            # update from pressing a button created by the bot
            logger.info("Request recognized as callback query")
            callback_id, payload = CallbackData.decode_callback_data(update.callback_query.data)

            if callback_id == CallbackData.RandomCoffeeNewParticipant:
                self._random_coffee_new_participant(callback_query=update.callback_query)
                # TODO: https://core.telegram.org/bots/api#answercallbackquery
            elif callback_id == CallbackData.RandomCoffeeSuccessfulMeeting:
                self._random_coffee_set_result(
                    payload=payload,
                    result=CallbackData.RandomCoffeeSuccessfulMeeting
                )
            elif callback_id == CallbackData.RandomCoffeeUnsuccessfulMeeting:
                self._random_coffee_set_result(
                    payload=payload,
                    result=CallbackData.RandomCoffeeUnsuccessfulMeeting
                )
        elif update.message is not None:
            logger.info("Request recognized as chat message")

            user = User(
                user_id=update.message.from_user.id,
                first_name=update.message.from_user.first_name,
                last_name=update.message.from_user.last_name,
                username=update.message.from_user.username
            )

            # add user to storage (it is a job of storage adapter to optimize if user is already there)
            self._storage_adapter.add_user(user=user)

            if update.message.chat.type == 'private':
                self._storage_adapter.add_chat(
                    chat_id=update.message.chat_id,
                    private=True,
                    user_id=update.message.from_user.id
                )
            if not self.introduced:
                logger.info(f"This is a first message in chat since start for {self.__class__}"
                            f" - sending introduction message")
                self._tg_presenter.send_message(
                    chat_id=update.message.chat_id,
                    message=self._storage_adapter.get_first_introduction_message()
                )
                # self.set_chat_id(update.message.chat_id)
            else:
                return

        elif update.message is not None and update.message.chat.type == 'private':
            logger.info("Request recognized as private message")
            self._add_private_chat_id(
                user_id=update.message.from_user.id,
                chat_id=update.message.chat_id
            )

    def _random_coffee_new_participant(self, callback_query: telegram.CallbackQuery):
        user = User(
            user_id=callback_query.from_user.id,
            username=callback_query.from_user.username,
            first_name=callback_query.from_user.first_name,
            last_name=callback_query.from_user.last_name
        )
        self._rc_manager.new_participant(user=user)

    def _random_coffee_set_result(self, payload: CallbackData.CallbackDataType, result: str):
        self._rc_manager.new_meeting_result(callback_payload=payload, result=result)
