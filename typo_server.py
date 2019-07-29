#!/usr/bin/env python3

from srv import WebServer, Controller
from srv.Database import JsonDatabase
from srv.SessionMgr import SessionMgr
import logging
from common import utils

DB_FILE = "db.json"
utils.setupLogger()
session_mgr = SessionMgr()
db = JsonDatabase(DB_FILE)
db.load()
logging.info("Server started")
controller = Controller.Controller(db=db, session_mgr=session_mgr)
srv = WebServer.WebServer(controller)
srv.run()
