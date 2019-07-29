import attr


@attr.s
class ClientState:
    client_id = attr.ib()
    ws_connection = attr.ib(default=None)
    client_info = attr.ib(default=None)


@attr.s
class GameSession():
    clients = attr.ib(default={}, init=False)

    def hasClient(self, client_id):
        return client_id in self.clients

    def getClientState(self, client_id: str):
        if not self.hasClient(client_id):
            return None
        return self.clients[client_id]

    def addClient(self, clientState: ClientState):
        self.clients[clientState.client_id] = clientState


@attr.s
class SessionMgr:
    sessions = attr.ib(default={})
    searching_for_game = attr.ib(default={})

    def addToSearching(self, client: ClientState):
        if client.client_id not in self.searching_for_game:
            self.searching_for_game[client.client_id] = client

    def isSearching(self, client_id: str):
        return client_id in self.searching_for_game

    def tryToMatch(self):
        if len(self.searching_for_game) < 2:
            return False
        clients_id_matched = list(self.searching_for_game.keys())[:2]
        clients_matched = []
        for client_id in clients_id_matched:
            client = self.searching_for_game.pop(client_id)
            clients_matched.append(client)
        return self.match(clients_matched)

    def match(self, clients):
        self.startGameSession(clients)
        return True

    def startGameSession(self, clients):
        session = GameSession()
        for client in clients:
            session.addClient(client)
        for client in clients:
            self.sessions[client.client_id] = session

    def getGameSession(self, client_id: str):
        return self.sessions.get(client_id, None)

    def endGameSession(self, client_id: str):
        session = self.getGameSession(client_id)
        for client in session.clients:
            self.sessions.pop(client)

    def getClientMates(self, client_id):
        """
        Return other clients info connected to game session
        """
        session = self.getGameSession(client_id)
        return list(filter(lambda x: x != client_id, session.clients.keys()))
