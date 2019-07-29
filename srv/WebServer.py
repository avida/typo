#!/usr/bin/env python3
from aiohttp import web
import asyncio
import logging
import json


class WebServer():
    def __init__(self, controller):
        self.controller = controller
        self.app = web.Application()
        self.runner = None
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        self.app.add_routes([
            web.get('/', self.handler),
            web.get('/register', self.handler),
            web.post('/register', self.handler),
            web.get('/session', self.ws_handler),
            web.get('/info', self.info_handler),
        ])

    async def info_handler(self, request):
        info = self.controller.getInfo()
        return web.Response(text=info)
        
    async def handler(self, request):
        res = self.controller.playerRegister(request.query)
        return web.Response(text=f"{json.dumps(res)}")

    async def ws_handler(self, request):
        ws = web.WebSocketResponse()
        client_id = request.headers["id"]
        await ws.prepare(request)
        await self.controller.sessionStarted(client_id, ws)
        try:
            async for msg in ws:
                await self.controller.messageReceived(msg, ws)
        except Exception as e:
            logging.info(f"except: {e} whle while processing {client_id} connection")
            await self.controller.playerDisconnected(client_id)
        return ws

    async def _run(self):
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, 'localhost', 8080)
        await site.start()

    def run(self):
        self.loop.create_task(self._run())
        self.loop.run_forever()

    async def _shutdown(self):
        await self.runner.cleanup()
        await self.runner.shutdown()
        self.loop.stop()

    def stop(self):
        asyncio.run_coroutine_threadsafe(self._shutdown(), self.loop)
