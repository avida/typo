import logging
import asyncio
from common.crypto_utils import (generateECKey, serializePublicKey,
                                 serializeECKey, loadECKey, toBase64,
                                 sign, fromBase64)


class Controller:
    def __init__(self, web_client, db, loop):
        self.web_client = web_client
        self.loop = loop
        self.db = db

    async def on_message(self, message):
        pass

    async def main(self):
        while True:
            try:
                res = await self.register()
                logging.info(res)
                ws = await self.web_client.openWSConnection(
                    "ws://localhost:8080/session",
                    headers={"id": res["id"]})
                logging.info("connected")
                cntr = 0
                while True:
                    try:
                        msg = await ws.receive()
                        logging.info(f"response: {msg.data}")
                        await asyncio.sleep(1)
                        logging.info(f"send {cntr}")
                        await ws.send_str(f"Hi {cntr}")
                    except Exception as e:
                        logging.info(f"e: {e}")
                    cntr += 1
                break
            except Exception as e:
                logging.warn(f"Unexpected error: {e}")
                await asyncio.sleep(1)

    def register(self):
        key = self.db.getUserInfo("key")
        if key is None:
            logging.info("generating key")
            key = generateECKey()
            self.db.storeUserInfo(
                "key", {"key": toBase64(serializeECKey(key))})
            self.db.save()
        else:
            logging.info("loading key")
            key = loadECKey(fromBase64(key["key"]))

        key_data = serializePublicKey(key.public_key())
        key_str = toBase64(key_data)
        key_signature = sign(key_data, key)
        key_signature = toBase64(key_signature)
        return self.web_client.sendGetRequest(
            "http://localhost:8080/register",
            query={
                "key": key_str,
                "signature": key_signature})
