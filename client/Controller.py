import logging 
import asyncio 

class Controller:
    def __init__(self, web_client, loop):
        self.web_client = web_client
        self.loop = loop

    async def main(self):
        while True:
            res = await self.register()
            logging.info(res)
            await asyncio.sleep(3)

    def register(self):
        return self.web_client.sendGetRequest("http://localhost:8080/register", query={"key": "dummyKey"})
