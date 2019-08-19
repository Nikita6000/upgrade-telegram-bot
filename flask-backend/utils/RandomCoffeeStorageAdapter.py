from typing import List, Dict, Optional
from utils.RandomCoffeeParticipant import RandomCoffeeParticipant
import logging

logger = logging.getLogger(__name__)


class RandomCoffeeStorageAdapter:

    def __init__(self) -> None:
        self._participants: List[RandomCoffeeParticipant] = []
        self._meetings_history: Dict[str, Dict[str, str]] = {}
        self._user_id_to_private_chat_id: Dict[str, str] = {}

    def get_unassigned_participants(self) -> List[RandomCoffeeParticipant]:
        return list(filter(lambda p: p.unassigned, self._participants))

    def add_participant(self, new_participant: RandomCoffeeParticipant) -> None:
        logger.info(f"New participant: id {new_participant.id}, name {new_participant.first_name}, "
                    f"username {new_participant.user_name}")
        if new_participant.id not in map(lambda p: p.id, self._participants):
            self._participants.append(new_participant)

    def remove_participant_by_id(self, id_to_remove) -> None:
        logger.info(f"Removing participant with id {id_to_remove}")
        index_to_delete = None
        for i, participant in enumerate(self._participants):
            if participant.id == id_to_remove:
                index_to_delete = i
        if index_to_delete is not None:
            self._participants.pop(index_to_delete)

    def set_participant_status(self, participant_id: str, unassigned: bool) -> None:
        for i, participant in enumerate(self._participants):
            if participant.id == participant_id:
                participant.unassigned = unassigned

    def set_meeting_result(self, group_id: str, participant_id: str, result: str):
        if group_id not in self._meetings_history:
            self._meetings_history[group_id] = {}
        self._meetings_history[group_id][participant_id] = result

    def add_private_chat_id(self, user_id, chat_id) -> None:
        logger.info(f"New private chat added with chat_id: {chat_id} for user_id: {user_id}")
        self._user_id_to_private_chat_id[user_id] = chat_id

    def get_private_chat_id(self, user_id: str) -> Optional[str]:
        return self._user_id_to_private_chat_id.get(user_id)
