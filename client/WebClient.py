import logging
import aiohttp
import asyncio
import json
from urllib.parse import urlsplit, urlunsplit, urlencode
from http import HTTPStatus

# Based on this table: https://docs.python.org/3.6/library/urllib.parse.html#urllib.parse.urlsplit
URLIB_QUERY_INDEX = 3

class WebClient:
    def __init__(self, loop):
        self.cntr = 0
        self.loop = loop

    @staticmethod
    async def _send_get(url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != HTTPStatus.OK:
                    logging.info(f"Unexpected status: {response.status}")
                    return {}
                text = await response.text()
                return json.loads(text)

    def sendGetRequest(self, url, query=None):
        url = list(urlsplit(url))
        if query is not None:
            query = urlencode(query)
            url[URLIB_QUERY_INDEX] = query
        url = urlunsplit(url)
        return self.loop.create_task(self._send_get(url))

    @staticmethod
    async def _send_post(url, data):
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data) as response:
                text = await response.text()
                return text

    def sendPostRequest():
        return self.loop.create_task(self._send_post(url,data))
    
    async def openWS(self, url):
        async with aiohttp.ClientSession() as session:
            while True:
                try:
                    ws = await session.ws_connect(url)
                    logging.info("Connected")
                    break
                except Exception as e:
                    logging.info(f"exception: {e}")
                    await asyncio.sleep(1)
            while True:
                await ws.send_str(f"Hi {self.cntr}")
                self.cntr += 1
                await asyncio.sleep(1)
                msg = await ws.receive()
                logging.info(f"response: {msg.data}")
        
    def openWSConnection(self, url):
        self.loop.create_task(self.openWS(url))
