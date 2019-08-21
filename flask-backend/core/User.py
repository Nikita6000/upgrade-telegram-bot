from typing import Optional


class User:
    """ A wrapper with basic info about user"""
    def __init__(self,
                 user_id: str,
                 first_name: str,
                 last_name: Optional[str],
                 username: Optional[str],
                 private_chat_id: Optional[str] = None):

        self.id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.private_chat_id = private_chat_id
