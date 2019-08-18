from flask_restful import Resource
import logging

logger = logging.getLogger(__name__)


class HelloWorld(Resource):
    def get(self):
        return "Hello World!"
