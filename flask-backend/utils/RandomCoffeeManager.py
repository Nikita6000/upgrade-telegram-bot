from utils.RandomCoffeeStorageAdapter import RandomCoffeeStorageAdapter
from utils.RandomCoffeeParticipant import RandomCoffeeParticipant
from utils.RandomCoffeeGroup import RandomCoffeeGroup
from utils.TelegramPresenter import TelegramPresenter
from utils.CallbackData import CallbackData
import random
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class RandomCoffeeManager:

    def __init__(self,
                 storage_adapter: RandomCoffeeStorageAdapter,
                 telegram_presenter: TelegramPresenter,
                 chat_id: Optional[str] = None) -> None:
        # adapters for storage and telegram api
        self._storage_adapter = storage_adapter
        self._telegram_presenter = telegram_presenter

        # info about main chat
        self.introduced = False
        self._chat_id: Optional[str] = chat_id

        # task scheduler
        self._scheduler = BackgroundScheduler()
        self._scheduler.add_job(self._pick_groups, 'interval', minutes=8)
        self._scheduler.start()

    def set_chat_id(self, chat_id: Optional[str]) -> None:
        logger.info(f"Setting chat id for Random Coffee to {chat_id}")
        self._chat_id = chat_id

    def _add_private_chat_id(self, user_id: str, chat_id: str) -> None:
        self._storage_adapter.add_private_chat_id(user_id=user_id, chat_id=chat_id)

    def new_telegram_update(self, update) -> None:

        if update.callback_query is not None:
            logger.info("Request recognized as callback")
            callback_id, payload = CallbackData.decode_callback_data(update.callback_query.data)

            if callback_id == CallbackData.RandomCoffeeNewParticipant:
                participant = RandomCoffeeParticipant(
                    user_id=update.callback_query.from_user.id,
                    user_name=update.callback_query.from_user.username,
                    first_name=update.callback_query.from_user.first_name,
                    last_name=update.callback_query.from_user.last_name
                )
                self._new_participant(participant)
            elif callback_id == CallbackData.RandomCoffeeSuccessfulMeeting:
                self._storage_adapter.set_meeting_result(
                    group_id=payload.get('group_id'),
                    participant_id=payload.get('participant_id'),
                    result=CallbackData.RandomCoffeeSuccessfulMeeting
                )
            elif callback_id == CallbackData.RandomCoffeeUnsuccessfulMeeting:
                self._storage_adapter.set_meeting_result(
                    group_id=payload.get('group_id'),
                    participant_id=payload.get('participant_id'),
                    result=CallbackData.RandomCoffeeUnsuccessfulMeeting
                )
        elif update.message is not None and update.message.chat.type != 'private':
            logger.info("Request recognized as chat message")

            if not self.introduced:
                logger.info("This is a first message in chat since start - sending introduction message")
                self.set_chat_id(update.message.chat_id)
            else:
                return

            text = "Hi! This is a quick and dirty test of core logic for Random Coffee\n\n"
            text += "Please press sign-up to add yourself to the list of participants.\n\n"
            text += " - Bot will announce groups of 2, 3, 4 or 5 people every 8 minutes" \
                    " (if at least 2 participants are free)\n"
            text += " - Bot will also ask you via personal message for the result after your time is up" \
                    " (please write something to the bot first for this to work)\n"
            self._telegram_presenter.send_message(
                chat_id=self._chat_id,
                text=text,
                reply_markup_constr=[
                    [('Sign-up for Random Coffee',
                      CallbackData.make_data_str(CallbackData.RandomCoffeeNewParticipant))]
                ]
            )
            self.introduced = True
        elif update.message is not None and update.message.chat.type == 'private':
            logger.info("Request recognized as private message")
            self._add_private_chat_id(
                user_id=update.message.from_user.id,
                chat_id=update.message.chat_id
            )

    def _pick_groups(self) -> None:
        unassigned_participants = self._storage_adapter.get_unassigned_participants()
        created_groups = []

        while len(unassigned_participants) >= 2:
            if len(unassigned_participants) > 6 and random.random() < 0.05:
                # create group of 5
                group = random.sample(unassigned_participants, 5)
                rc_group = RandomCoffeeGroup(participants=group, days_to_finish=7)
            elif len(unassigned_participants) > 5 and random.random() < 0.1:
                # create group of 4
                group = random.sample(unassigned_participants, 4)
                rc_group = RandomCoffeeGroup(participants=group, days_to_finish=7)
            elif len(unassigned_participants) > 4 and random.random() < 0.3:
                # create group of 3
                group = random.sample(unassigned_participants, 3)
                rc_group = RandomCoffeeGroup(participants=group, days_to_finish=3)
            else:
                # create group of 2
                group = random.sample(unassigned_participants, 2)
                rc_group = RandomCoffeeGroup(participants=group, days_to_finish=3)

            created_groups.append(rc_group)
            for participant in group:
                unassigned_participants.remove(participant)

            self._scheduler.add_job(
                func=self._conclude_group,
                trigger='date',
                kwargs={'group': rc_group},
                run_date=datetime.today() + timedelta(minutes=rc_group.days_to_finish)
            )

        # notify participants of new groups
        if len(created_groups) > 0:
            announcement_msg = "New groups for Random Coffee have been formed!\n\n"
            for i, group in enumerate(created_groups):
                announcement_msg += f"Group #{i + 1}: " + " ".join(
                    map(lambda p: self._telegram_presenter.get_name_as_mention(p), group.participants)
                )
                announcement_msg += "\n\n"

            self._telegram_presenter.send_message(
                text=announcement_msg,
                chat_id=self._chat_id,
                parse_mode="Markdown"
            )

    def _conclude_group(self, group: RandomCoffeeGroup) -> None:
        for participant in group.participants:
            private_chat_id = self._storage_adapter.get_private_chat_id(participant.id)

            if private_chat_id is not None:
                self._telegram_presenter.send_message(
                    chat_id=private_chat_id,
                    text="Yo! How was your last Random Coffee? Did you meet?",
                    reply_markup_constr=[
                        [
                            ("We did not meet", CallbackData.make_data_str(
                                callback_id=CallbackData.RandomCoffeeUnsuccessfulMeeting,
                                payload={"group_id": group.group_id, "participant_id": participant.id}
                            ))
                        ],
                        [
                            ("Yep, we did", CallbackData.make_data_str(
                                callback_id=CallbackData.RandomCoffeeSuccessfulMeeting,
                                payload={"group_id": group.group_id, "participant_id": participant.id}
                            ))
                        ]
                    ]
                )

            self._storage_adapter.set_participant_status(
                participant_id=participant.id, unassigned=True
            )

    def _new_participant(self, participant: RandomCoffeeParticipant) -> None:
        self._storage_adapter.add_participant(participant)

