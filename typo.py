#!/usr/bin/env python3
import asyncio 
import logging
from client import WebClient
from common import utils
from client import Controller

utils.setupLogger()
logging.info("client started")
loop = asyncio.get_event_loop()
client = WebClient.WebClient(loop)
client_controller = Controller.Controller(client, loop)
loop.create_task(client_controller.main())
loop.run_forever()
