#!/usr/bin/env python3

from srv import WebServer, Controller
from srv.Database import JsonDatabase
import logging
from common import utils

DB_FILE = "db.json"
utils.setupLogger()
db = JsonDatabase(DB_FILE)
db.load()
logging.info("Server started")
controller = Controller.Controller(db)
srv = WebServer.WebServer(controller)
srv.run()



