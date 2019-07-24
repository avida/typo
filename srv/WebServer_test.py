from srv.WebServer import WebServer
from srv.Controller import Controller
from threading import Thread
from http import HTTPStatus
import time
import pytest
import requests
import json
from unittest.mock import Mock

class ThreadServer(Thread):
    def __init__(self, controller):
        Thread.__init__(self)
        self.controller = controller

    def run(self):
        self.srv = WebServer(self.controller)
        self.srv.run()

    def stop(self):
        self.srv.stop()
        self.join()

@pytest.mark.timeout(3)
def test_stop():
    t = ThreadServer(None)
    t.start()
    time.sleep(.1)
    t.stop()

@pytest.mark.timeout(3)
def test_handler():
    controller = Controller()
    controller.playerRegister = Mock(return_value="any")
    t = ThreadServer(controller)
    t.start()
    time.sleep(.1)
    r = requests.get("http://localhost:8080/register?key=aaa")
    assert r.status_code == HTTPStatus.OK
    resp = json.loads(r.text)
    assert resp == "any"
    controller.playerRegister.assert_called_once_with("aaa")
    t.stop()

