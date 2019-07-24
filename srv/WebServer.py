#!/usr/bin/env python3
from aiohttp import web
import asyncio
import logging
import json

class WebServer():
    def __init__(self, controller):
        self.controller = controller
        self.app = web.Application()

        self.app.add_routes([
                    web.get('/', self.handler),
                    web.get('/register', self.handler),
                    web.post('/register', self.handler),
                    web.get('/session', self.ws_handler),
                       ])

    async def handler(self, request):
        if "key" not in request.query:
            return {"error": "No key parameter"}
        res = self.controller.playerRegister(request.query["key"])
        return web.Response(text=f"{json.dumps(res)}")

    async def ws_handler(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        async for msg in ws:
            logging.info(msg.data)
            await ws.send_str("Message received")
        return ws

    def run(self):
        web.run_app(self.app)
        

