from typing import Optional


class RandomCoffeeParticipant:
    def __init__(self,
                 user_id: str,
                 first_name: str,
                 last_name: Optional[str],
                 user_name: Optional[str],
                 unassigned: bool = True):
        self.unassigned = unassigned
        self.id: str = user_id
        self.first_name: str = first_name
        self.last_name: Optional[str] = last_name
        self.user_name: Optional[str] = user_name
