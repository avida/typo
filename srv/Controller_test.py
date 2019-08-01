from srv.Controller import Controller
import pytest
from unittest.mock import Mock
from common.crypto_utils import (generateECKey, serializePublicKey,
                                 toBase64, sign, getMD5)
from utils import makeErrorResponse


class MockObject:
    def __setattr__(self, attr, val):
        self.__dict__[attr] = val


@pytest.fixture
def registration_data():
    private_key = generateECKey()
    key_data = serializePublicKey(private_key.public_key())
    signature = sign(key_data, private_key)
    signature = toBase64(signature)
    key = toBase64(key_data)
    return {"key": key,
            "key_data": key_data,
            "private_key": private_key,
            "signature": signature}


@pytest.fixture
def mock_db():
    db = MockObject()
    db.getUserInfo = Mock(return_value=None)
    db.storeUserInfo = Mock(return_value=True)
    return db


def test_playerRegisterInvalidKey():
    key = {"key": "someKey"}
    res = Controller().playerRegister(key)
    assert res == makeErrorResponse("Invalid key")


def test_playerRegisterNoSignature(registration_data):
    controller = Controller()
    del registration_data["signature"]
    res = controller.playerRegister(registration_data)
    assert res == makeErrorResponse("No signature")


def test_playerRegisterSignatureDoesntMatch(registration_data):
    controller = Controller()
    registration_data["signature"] = toBase64(
        sign(b"some data", registration_data["private_key"]))
    res = controller.playerRegister(registration_data)
    assert res == makeErrorResponse("Signature doesnt match")


def test_playerRegister(registration_data, mock_db):
    controller = Controller(db=mock_db)
    res = controller.playerRegister(registration_data)
    assert res["result"] == "ok"
    mock_db.getUserInfo.assert_called_once_with(
        getMD5(registration_data["key_data"]))
    mock_db.storeUserInfo.assert_called_once()


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
