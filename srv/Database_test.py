from srv.Database import JsonDatabase
import pytest

DB_FILE = "test.json"
userId = "dummy_id"
userInfo = {"name": "userbot"}


@pytest.fixture(scope="function")
def fx():
    yield fx
    JsonDatabase.cleanup(DB_FILE)


def test_store_get(fx):
    db = JsonDatabase(DB_FILE)
    db.storeUserInfo(userId, userInfo)
    ui = db.getUserInfo(userId)
    assert ui == userInfo


def test_save_load(fx):
    db = JsonDatabase(DB_FILE)
    db.storeUserInfo(userId, userInfo)
    db.save()
    db = JsonDatabase(DB_FILE)
    assert db.getUserInfo(userId) is None
    db.load()
    assert db.getUserInfo(userId) == userInfo
