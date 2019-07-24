#!/usr/bin/env python3

from srv import Database, WebServer, Controller
import logging
from common import utils

utils.setupLogger()
logging.info("Server started")
controller = Controller.Controller()
srv = WebServer.WebServer(controller)
srv.run()



