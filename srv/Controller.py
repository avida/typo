import logging
from common.crypto_utils import loadPublicKey, fromBase64, verify


class Controller:
    def __init__(self):
        pass
    def playerRegister(self, query):
        try:
            key = query["key"]
            signature = query["signature"]
            signature = fromBase64(signature)
            if signature is None:
                logging.info("Invalid signature")
                return {"result": "error"}
            key_data = fromBase64(key)
            key = loadPublicKey(key_data)
            if key is None:
                logging.info("Invalid key")
                return {"result": "error"}
            if not verify(key_data, signature, key):
                logging.error("Signature doesnt math")
                return {"result": "error"}
        except Exception as e:
            return {"result":"error","message": str(e) }
        return {"result": "ok"}

    def playerDisconnected(self, key):
        return {"result": "ok"}

    def playerMsgReceived(self, key , message):
        return {}

