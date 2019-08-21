from typing import List, Dict
from core.CallbackData import CallbackData
from core.StorageAdapter import StorageAdapter
from core.TelegramMessageWrapper import TelegramMessageWrapper
from random_coffee.RandomCoffeeParticipant import RandomCoffeeParticipant
import logging

logger = logging.getLogger(__name__)


class RandomCoffeeStorageAdapter(StorageAdapter):
    def __init__(self) -> None:
        super().__init__()

        self._participants: List[RandomCoffeeParticipant] = []
        self._meetings_history: Dict[str, Dict[str, str]] = {}

    def get_unassigned_participants(self) -> List[RandomCoffeeParticipant]:
        """ Returns all participants that are currently not assigned into groups """
        return list(filter(lambda p: p.unassigned, self._participants))

    def add_participant(self, new_participant: RandomCoffeeParticipant) -> None:
        """ Adds new participant to the Random Coffee """
        logger.info(f"New participant: id {new_participant.id}, name {new_participant.first_name}, "
                    f"username {new_participant.username}")
        if new_participant.id not in map(lambda p: p.id, self._participants):
            self._participants.append(new_participant)

    def remove_participant_by_id(self, id_to_remove) -> None:
        """ Remove participant from Random Coffee """
        logger.info(f"Removing participant with id {id_to_remove}")
        index_to_delete = None
        for i, participant in enumerate(self._participants):
            if participant.id == id_to_remove:
                index_to_delete = i
        if index_to_delete is not None:
            self._participants.pop(index_to_delete)

    def set_participant_status(self, participant_id: str, unassigned: bool) -> None:
        """
            Sets the participant to unassigned=False (currently have group to meet with)
            or unassigned=True (currently have no group to meet with, waiting to be assigned)
        """
        for i, participant in enumerate(self._participants):
            if participant.id == participant_id:
                participant.unassigned = unassigned

    def set_meeting_result(self, group_id: str, participant_id: str, result: str):
        if group_id not in self._meetings_history:
            self._meetings_history[group_id] = {}
        self._meetings_history[group_id][participant_id] = result

    @staticmethod
    def get_first_introduction_message() -> TelegramMessageWrapper:
        text = "Hi! This is a quick and dirty test of core logic for Random Coffee\n\n"
        text += "Please press sign-up to add yourself to the list of participants.\n\n"
        text += " - Bot will announce groups of 2, 3, 4 or 5 people every 8 minutes" \
                " (if at least 2 participants are free)\n"
        text += " - Bot will also ask you via personal message for the result after your time is up" \
                " (please write something to the bot first for this to work)\n"

        msg = TelegramMessageWrapper(msg_text=text, inline_reply_markup=[
            [('Sign-up for Random Coffee',
              CallbackData.make_data_str(CallbackData.RandomCoffeeNewParticipant))]
            ]
        )

        return msg
