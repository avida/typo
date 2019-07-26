#!/usr/bin/env python3
import asyncio
import logging
from client import WebClient
from common import utils
from client import Controller
from plumbum.cli import Application, SwitchAttr, switch
from srv.Database import JsonDatabase
import os

DB_FILE = "typo.json"


class App(Application):
    config_dir = SwitchAttr(
        "config", str,  help="directory for storing config", default=".")

    def make_config_dir(self):
        if not os.path.isdir(self.config_dir):
            os.mkdir(self.config_dir)

    def main(self):
        self.make_config_dir()
        utils.setupLogger()
        logging.info("client started")
        loop = asyncio.get_event_loop()
        client = WebClient.WebClient(loop)
        db = JsonDatabase(os.path.join(self.config_dir, DB_FILE))
        db.load()
        client_controller = Controller.Controller(client, db, loop)
        loop.create_task(client_controller.main())
        loop.run_forever()


App.run()
