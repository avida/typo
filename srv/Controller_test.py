from srv.Controller import Controller


def test_playerRegister():
    key = {"key": "someKey"}
    res = Controller().playerRegister(key)
    assert res["result"] == "error"


def test_playerDisconnected():
    playerId = "someId"
    res = Controller().playerDisconnected(playerId)
    try:
        res.send(None)
    except StopIteration as e:
        res = e.value
        assert res["result"] == "ok"
    else:
        assert False
