from flask import request
from flask_restful import Resource
from core.RequestHandler import RequestHandler
import logging

logger = logging.getLogger(__name__)


class TelegramWebHook(Resource):
    def __init__(self, request_handler: RequestHandler):
        self._request_handler = request_handler

    def post(self):
        request_data = request.get_json(force=True)
        self._request_handler.process_request(request_data)
        return None
