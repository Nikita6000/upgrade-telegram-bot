from core.User import User


class RandomCoffeeParticipant(User):
    """ Wrapper around User for the Random Coffee feature """
    def __init__(self, user: User, unassigned: bool = True):

        super().__init__(**user.__dict__)

        self.unassigned = unassigned

