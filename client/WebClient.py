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
        self.session = None

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
    
    async def _openWS(self, url, **kvargs):
        while True:
            try:
                ws = await self.session.ws_connect(url, **kvargs)
                return ws
            except Exception as e:
                logging.info(f"exception: {e}")
                await asyncio.sleep(1)
        
    async def openWSConnection(self, url, **kvargs):
        if not self.session:
            self.session = aiohttp.ClientSession()
        res = await self.loop.create_task(self._openWS(url, **kvargs))
        return res

