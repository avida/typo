from srv.SessionMgr import ClientState, GameSession, SessionMgr


def test_client_state():
    state = ClientState("sdf", None, None)
    assert state


def test_game_session():
    client1 = ClientState("id1")
    client2 = ClientState("id2")
    session = GameSession()
    session.addClient(client1)
    session.addClient(client2)
    assert session.hasClient("id2")
    assert session.hasClient("id1")
    assert not session.hasClient("id3")


def test_session_mgr():
    client1 = ClientState("id1")
    client2 = ClientState("id2")
    session_mgr = SessionMgr()
    session_mgr.startGameSession((client1, client2))
    session = session_mgr.getGameSession("id2")
    assert session
    assert session_mgr.getGameSession("id1")
    assert session_mgr.getGameSession("id2")
    assert not session_mgr.getGameSession("id3")
    session_mgr.endGameSession("id2")
    assert not session_mgr.getGameSession("id1")
    assert not session_mgr.getGameSession("id2")


def test_game_search():
    client1 = ClientState("id1")
    client2 = ClientState("id2")
    session_mgr = SessionMgr()
    session_mgr.addToSearching(client1)
    assert session_mgr.isSearching(client1.client_id)
    assert not session_mgr.isSearching(client2.client_id)
    assert not session_mgr.tryToMatch()
    session_mgr.addToSearching(client2)
    assert session_mgr.isSearching(client2.client_id)
    assert not session_mgr.getGameSession("id1")
    assert not session_mgr.getGameSession("id2")
    assert session_mgr.tryToMatch()
    assert not session_mgr.isSearching(client1.client_id)
    assert not session_mgr.isSearching(client2.client_id)
    assert session_mgr.getGameSession("id1")
    assert session_mgr.getGameSession("id2")
    mates = session_mgr.getClientMates("id1")
    assert len(mates) == 1
    assert mates[0] == "id2"
