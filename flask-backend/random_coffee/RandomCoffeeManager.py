from random_coffee.RandomCoffeeStorageAdapter import RandomCoffeeStorageAdapter
from random_coffee.RandomCoffeeParticipant import RandomCoffeeParticipant
from random_coffee.RandomCoffeeGroup import RandomCoffeeGroup
from core.TelegramPresenter import TelegramPresenter
from core.CallbackData import CallbackData
from core.User import User
from core.TelegramMessageWrapper import TelegramMessageWrapper
import random
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from typing import Optional, Dict
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

    def new_participant(self, user: User) -> None:
        participant = RandomCoffeeParticipant(user=user)
        self._storage_adapter.add_participant(participant)

    def new_meeting_result(self, callback_payload: Dict, result: str):
        if 'group_id' in callback_payload and 'participant_id' in callback_payload:
            self._storage_adapter.set_meeting_result(
                group_id=callback_payload.get('group_id'),
                participant_id=callback_payload.get('participant_id'),
                result=result
            )

    def set_chat_id(self, chat_id: Optional[str]) -> None:
        logger.info(f"Setting chat id for Random Coffee to {chat_id}")
        self._chat_id = chat_id

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
                chat_id=self._chat_id,
                message=TelegramMessageWrapper(msg_text=announcement_msg, parse_mode="Markdown")
            )

    def _conclude_group(self, group: RandomCoffeeGroup) -> None:
        for participant in group.participants:
            private_chat_id = self._storage_adapter.get_private_chat_id(participant.id)

            if private_chat_id is not None:
                self._telegram_presenter.send_message(
                    chat_id=private_chat_id,
                    message=TelegramMessageWrapper(
                            msg_text="Yo! How was your last Random Coffee? Did you meet?",
                            inline_reply_markup=[
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
                )

            self._storage_adapter.set_participant_status(
                participant_id=participant.id, unassigned=True
            )
