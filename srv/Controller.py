import logging
from common.crypto_utils import loadPublicKey, fromBase64, verify, getMD5
from faker import Faker


class Controller:
    def __init__(self, db):
        self.db = db

    def playerRegister(self, query):
        try:
            key_str = query["key"]
            signature = query["signature"]
            signature_data = fromBase64(signature)
            if signature_data is None:
                logging.info("Invalid signature")
                return {"result": "error"}
            key_data = fromBase64(key_str)
            key = loadPublicKey(key_data)
            if key is None:
                logging.info("Invalid key")
                return {"result": "error"}
            if not verify(key_data, signature_data, key):
                logging.error("Signature doesnt math")
                return {"result": "error"}
        except Exception as e:
            return {"result": "error", "message": str(e)}
        client_id = getMD5(key_data)
        user_info = self.db.getUserInfo(client_id)
        if user_info is None:
            logging.info("generating user name")
            name = Faker("uk_UA").name().replace(" ", "_")
            self.db.storeUserInfo(client_id, {"name": name, "key": key_str})
        else:
            logging.info("user found")
            name = user_info["name"]
        return {"result": "ok", "id": client_id, "name": name}

    def playerDisconnected(self, client_id):
        if self.db is not None:
            user_info = self.db.getUserInfo(client_id)
            logging.info(f'Player {user_info["name"]} disconnected')
        return {"result": "ok"}

    async def sessionStarted(self, client_id, ws):
        await ws.send_str(f"hi, {client_id}")

    async def messageReceived(self, msg, ws):
        logging.info(msg.data)
        await ws.send_str(f"response {msg.data}")

    def playerMsgReceived(self, key, message):
        return {}
