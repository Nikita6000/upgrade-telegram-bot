from flask import Flask
from flask_restful import Api
from flask_cors import CORS
import logging
import os
from resources.api.v1.TelegramWebHook import TelegramWebHook
from credentials.telegram import BOT_TOKEN
from resources.HelloWorld import HelloWorld
from utils.RandomCoffeeManager import RandomCoffeeManager
from utils.RandomCoffeeStorageAdapter import RandomCoffeeStorageAdapter
from utils.TelegramPresenter import TelegramPresenter


logging_format = "[%(asctime)s] [%(process)d] [%(threadName)s] [%(levelname)s] - %(message)s"

if __name__ == '__main__':
    logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"), format=logging_format)
else:
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    if logger.hasHandlers():
        for handler in logger.handlers:
            handler.setFormatter(
                logging.Formatter(logging_format)
            )
    else:
        logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"), format=logging_format)


app = Flask(__name__, static_url_path='')
CORS(app)

api = Api(app)

rc_manager = RandomCoffeeManager(
    storage_adapter=RandomCoffeeStorageAdapter(),
    telegram_presenter=TelegramPresenter()
)

api.add_resource(TelegramWebHook, f'/{BOT_TOKEN}', resource_class_kwargs={'rc_manager': rc_manager})
api.add_resource(HelloWorld, '/')

if __name__ == '__main__':
    app.run(debug=True)  # ssl_context=('cert.pem', 'private_key.pem'))
