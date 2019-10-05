from typing import List, Dict, Optional
from core.CallbackData import CallbackData
from core.StorageAdapter import StorageAdapter
from core.TelegramMessageWrapper import TelegramMessageWrapper
from bot_services.random_coffee import RandomCoffeeParticipant
import logging

logger = logging.getLogger(__name__)


class RandomCoffeeStorageAdapter(StorageAdapter):
    def __init__(self, parent_storage_adapter: Optional[StorageAdapter] = None) -> None:
        super().__init__()

        # having the same methods isn't good enough. Since all storage is currently just a dictionaries,
        # link to the same objects, so that methods called on object of base class have affect on objects of this class
        if parent_storage_adapter is not None:
            self.__dict__.update(parent_storage_adapter.__dict__)

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
        """ Save result of the meeting (whether group have met or not) """
        if group_id not in self._meetings_history:
            self._meetings_history[group_id] = {}
        self._meetings_history[group_id][participant_id] = result

    def get_introduction_for_random_coffee(self,
                                           chat_id: str,
                                           markdown_mention: Optional[str] = None) -> TelegramMessageWrapper:
        """  Constructs intro message for Random Coffee. """
        if markdown_mention is not None:
            text = f"{markdown_mention} has initialized a game of Random Coffee for this chat " \
                f"and so became the first participant!\n\n"
        else:
            text = "A game of Random Coffee has been initialized for this chat.\n\n"
        text += "Please press sign-up to add yourself to the list of participants.\n\n"
        text += " - Bot will announce groups of 2, 3, 4 or 5 people every 8 minutes" \
                " (if at least 2 participants are free)\n"
        text += " - Bot will also ask you via personal message for the result after your time is up" \
                " (please write something to the bot first for this to work)\n"

        payload_id = self.add_callback_payload({
            'callback_id': CallbackData.RandomCoffeeNewParticipant,
            'chat_id': chat_id
        })

        msg = TelegramMessageWrapper(
            msg_text=text,
            parse_mode=TelegramMessageWrapper.parse_modes.Markdown,
            inline_reply_markup=[
                [('Sign-up for Random Coffee', payload_id)]
            ]
        )

        return msg
