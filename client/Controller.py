import logging 
import asyncio 
from common.crypto_utils import generateECKey, serializePublicKey, toBase64, sign

class Controller:
    def __init__(self, web_client, loop):
        self.web_client = web_client
        self.loop = loop

    async def main(self):
        while True:
            try:
                res = await self.register()
                logging.info(res)
                break
            except Exception as e:
                logging.warn(f"Unexpected error: {e}")

    def register(self):
        key = generateECKey()
        key_data = serializePublicKey(key.public_key())
        key_str = toBase64(key_data)
        key_signature = sign(key_data, key)
        key_signature = toBase64(key_signature)
        return self.web_client.sendGetRequest("http://localhost:8080/register", query={"key": key_str, "signature": key_signature})
