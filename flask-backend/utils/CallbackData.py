import json
from typing import Optional, Union, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class CallbackData:
    """ Simply stores all callback data used for buttons in telegram """

    RandomCoffeeNewParticipant = "1"

    RandomCoffeeSuccessfulMeeting = "2"

    RandomCoffeeUnsuccessfulMeeting = "3"

    @staticmethod
    def make_data_str(callback_id: str, payload: Optional[Union[str, Dict]] = None) -> str:
        data = {
            "callback_id": callback_id
        }
        if payload is not None:
            data['payload'] = payload

        return json.dumps(data)

    @staticmethod
    def decode_callback_data(data: str) -> Tuple[str, Optional[Union[str, Dict]]]:
        d = json.JSONDecoder()
        try:
            decoded = d.decode(data)
            return decoded['callback_id'], decoded.get('payload', {})
        except json.JSONDecodeError as e:
            logger.error(f"Json decoder error during decoding callback payload: {e}")
            return "0", {}
