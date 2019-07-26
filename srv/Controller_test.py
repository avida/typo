from srv.Controller import Controller


def test_playerRegister():
    key = {"key": "someKey"}
    res = Controller(None).playerRegister(key)
    assert res["result"] == "error"


def test_playerDisconnected():
    playerId = "someId"
    res = Controller(None).playerDisconnected(playerId)
    assert res["result"] == "ok"
