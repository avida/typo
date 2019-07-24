import logging

class Controller:
    def __init__(self):
        pass
    def playerRegister(self, key):
        logging.info(f"key is {key}")
        return {"result": "ok"}

    def playerDisconnected(self, key):
        return {}

    def playerMsgReceived(self, key , message):
        return {}

