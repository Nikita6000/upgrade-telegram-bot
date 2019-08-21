from random_coffee.RandomCoffeeParticipant import RandomCoffeeParticipant
from typing import Tuple
import uuid
import datetime


class RandomCoffeeGroup:
    def __init__(self,
                 participants: Tuple[RandomCoffeeParticipant],
                 days_to_finish: int):
        self.participants = participants
        self.group_id: str = str(uuid.uuid4())
        self.start_time = datetime.datetime.today()
        self.days_to_finish: int = days_to_finish
