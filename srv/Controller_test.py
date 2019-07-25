from srv.Controller import Controller
import json

def test_playerRegister():
    key = {"key": "someKey"}
    res = Controller().playerRegister(key)
    assert  res["result"] == "error"

def test_playerDisconnected():
    playerId = "someId"
    res = Controller().playerDisconnected(playerId)
    assert  res["result"] == "ok"
    
