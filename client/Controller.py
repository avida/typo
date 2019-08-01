import logging
import asyncio
from common.crypto_utils import (generateECKey, serializePublicKey,
                                 serializeECKey, loadECKey, toBase64,
                                 sign, fromBase64)
import sys
from functools import partial
from aiohttp import WSMsgType


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
                logging.info(f"My name is {res['name']}")
                ws = await self.web_client.openWSConnection(
                    "ws://localhost:8080/session",
                    headers={"id": res["id"]})
                logging.info("ws connected")
                self.loop.add_reader(sys.stdin,
                                     partial(Controller.user_data, self, ws))
                while True:
                    try:
                        msg = await ws.receive()
                        if msg.type == WSMsgType.CLOSED:
                            logging.info(f"msg closed")
                            break
                        logging.debug(f"{msg}")
                    except Exception as e:
                        logging.info(f"e: {e}")
                        self.loop.remove_reader(sys.stdin)
                        break
            except Exception as e:
                logging.error(f"except: {e}")
                await asyncio.sleep(1)

    def user_data(self, ws):
        line = sys.stdin.readline()
        line = line.strip()

        async def send_line(ws, line):
            logging.debug(f"line is {line}")
            await ws.send_str(line)
        self.loop.create_task(send_line(ws, line))

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
