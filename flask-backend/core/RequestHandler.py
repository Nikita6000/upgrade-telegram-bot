import telegram
from credentials.credentials import BOT_TOKEN
from core.StorageAdapter import StorageAdapter
from core.TelegramPresenter import TelegramPresenter
from bot_services.random_coffee.RandomCoffeeManager import RandomCoffeeManager
from bot_services.random_coffee.RandomCoffeeStorageAdapter import RandomCoffeeStorageAdapter
from typing import Optional, Set
import logging

logger = logging.getLogger(__name__)


class RequestHandler:

    def __init__(self,
                 storage_adapter: Optional[StorageAdapter] = None,
                 tg_presenter: Optional[TelegramPresenter] = None):
        # objects for communication with telegram
        self._bot = telegram.Bot(token=BOT_TOKEN)
        self._telegram_presenter = tg_presenter if tg_presenter is not None else TelegramPresenter(self._bot)

        # storage
        self._storage_adapter = storage_adapter if storage_adapter is not None else StorageAdapter()

        self._services = {
            RandomCoffeeManager.__name__: RandomCoffeeManager(
                storage_adapter=RandomCoffeeStorageAdapter(self._storage_adapter),
                telegram_presenter=self._telegram_presenter
            )
        }
        # feature managers
        # self._rc_manager_dict: Dict[str, RandomCoffeeManager] = rc_manager_dict if rc_manager_dict is not None else {}

        # self.introduced_chat_ids: Set = set()

    def process_request(self, json_request) -> None:

        update = telegram.Update.de_json(json_request, self._bot)

        if update.callback_query is not None:
            # callback_query is an update from pressing a button created by the bot
            logger.info("Request recognized as callback query")

            # each callback can carry up to 64 bytes in callback_data. I use it as id for useful data ("payload")
            payload = self._storage_adapter.get_callback_payload(update.callback_query.data)
            if payload is None:
                logger.warning(f"Received callback with unrecognized id. Callback_query: {update.callback_query}")
                return

            service_name = payload['service_name']

            user = self._storage_adapter.get_or_create_user(update.callback_query.from_user)

            self._services[service_name].process_callback_query(update.callback_query)

            # # init User object for user who pressed the button
            # user = User(
            #     user_id=update.callback_query.from_user.id,
            #     username=update.callback_query.from_user.username,
            #     first_name=update.callback_query.from_user.first_name,
            #     last_name=update.callback_query.from_user.last_name,
            #     storage_adapter=self._storage_adapter
            # )


            # if callback_id == CallbackData.NewRandomCoffeeGame:
            #     chat_id = payload['chat_id']
            #
            #     if chat_id not in self._rc_manager_dict:
            #         self._rc_manager_dict[chat_id] = RandomCoffeeManager(
            #             storage_adapter=RandomCoffeeStorageAdapter(parent_storage_adapter=self._storage_adapter),
            #             telegram_presenter=self._telegram_presenter,
            #             chat_id=chat_id,
            #             first_participant=user
            #         )
            #
            #     # all necessary info will be sent as a message, so sent nothing as answer
            #     update.callback_query.answer(text=None)
            #
            # elif callback_id == CallbackData.RandomCoffeeNewParticipant:
            #     self._rc_manager_dict[payload['chat_id']].add_participant(user=user)
            #     update.callback_query.answer(text="You are now in the game!")
            # elif callback_id == CallbackData.RandomCoffeeSuccessfulMeeting:
            #     self._rc_manager_dict[payload['chat_id']].add_meeting_result(
            #         callback_payload=payload,
            #         result=CallbackData.RandomCoffeeSuccessfulMeeting
            #     )
            #     update.callback_query.answer(text="Great!")
            # elif callback_id == CallbackData.RandomCoffeeUnsuccessfulMeeting:
            #     self._rc_manager_dict[payload['chat_id']].add_meeting_result(
            #         callback_payload=payload,
            #         result=CallbackData.RandomCoffeeUnsuccessfulMeeting
            #     )
            #     update.callback_query.answer(text="That's unfortunate :(")
        elif update.message is not None:
            logger.info(f"Request recognized as chat message: {update.message}")

            if update.message.chat.type == 'private':
                self._storage_adapter.add_chat(
                    chat_id=update.message.chat_id,
                    private=True,
                    user_id=update.message.from_user.id
                )

            user = self._storage_adapter.get_or_create_user(update.message.from_user)

            for service in self._services.values():
                service.maybe_process_message(update.message)

            # user = User(
            #     user_id=update.message.from_user.id,
            #     first_name=update.message.from_user.first_name,
            #     last_name=update.message.from_user.last_name,
            #     username=update.message.from_user.username,
            #     storage_adapter=self._storage_adapter
            # )

            # add user to storage (it is a job of storage adapter to optimize if user is already there)
            # self._storage_adapter.add_user(user_id=user.id, user_info=user)

            # if update.message.chat_id not in self.introduced_chat_ids:
            #     logger.info(f"This is a first message in chat since start for {self.__class__}"
            #                 f" - sending introduction message")
            #     self._telegram_presenter.send_message(
            #         chat_id=update.message.chat_id,
            #         message=self._storage_adapter.get_first_introduction_message(
            #             chat_id=update.message.chat_id,
            #             private=update.message.chat.type == 'private',
            #             user_first_name=user.first_name
            #         )
            #     )
            #     self.introduced_chat_ids.add(update.message.chat_id)
