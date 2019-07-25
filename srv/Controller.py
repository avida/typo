import logging
from common.crypto_utils import loadPublicKey, fromBase64


class Controller:
    def __init__(self):
        pass
    def playerRegister(self, key):
        key = fromBase64(key)
        logging.info(f"key is {key}")
        key = loadPublicKey(key)
        logging.info(f"key loaded: {key != None}")
        return {"result": "ok"}

    def playerDisconnected(self, key):
        return {"result": "ok"}

    def playerMsgReceived(self, key , message):
        return {}

