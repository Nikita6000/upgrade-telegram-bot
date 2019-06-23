from flask import Flask
from flask_restful import Api
from flask_cors import CORS
import logging
import os

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

app = Flask(__name__, static_url_path='')
CORS(app)

api = Api(app)

if __name__ == '__main__':
    app.run(debug=True, )
