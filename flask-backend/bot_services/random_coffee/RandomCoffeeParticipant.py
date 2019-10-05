from core.User import User


class RandomCoffeeParticipant(User):
    """ Wrapper around User for the Random Coffee feature """
    def __init__(self, user: User, unassigned: bool = True):
        self.__dict__.update(user.__dict__)
        self.unassigned = unassigned

