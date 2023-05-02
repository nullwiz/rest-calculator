from abc import ABC, abstractmethod
import requests
from restcalculator.exceptions.custom_exceptions import ExternalServiceException
from flask import current_app as app
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AbstractRandomStringService(ABC):

    @abstractmethod
    def getString():
        raise NotImplemented


class RandomStringService(AbstractRandomStringService):

    @staticmethod
    def getString():
        api_key = app.config["RANDOM_STRING_API_KEY"]
        # Create the schema for the JSON-RPC request
        data = {
            "jsonrpc": "2.0",
            "method": "generateStrings",
            "params": {
                "apiKey": api_key,
                "n": 1,
                "length": 8,
                "characters": "abcdefghijklmnopqrstuvwxyz"
            },
            "id": 1
        }
        r = requests.post(
            app.config["RANDOM_STRING_API_URL"], json=data, timeout=20)
        if r.status_code == 200:
            return r.json()['result']['random']['data'][0]
        else:
            raise ExternalServiceException("Random string service failed")
