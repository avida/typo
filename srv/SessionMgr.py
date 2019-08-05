import attr


@attr.s
class ClientState:
    client_id = attr.ib()
    ws_connection = attr.ib(default=None)
    client_info = attr.ib(default=None)


@attr.s
class GameSession():
    clients = attr.ib(factory=dict, init=False)

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
    sessions = attr.ib(factory=dict)
    searching_for_game = attr.ib(factory=dict)

    def findClientState(self, client_id):
        if self.isSearching(client_id):
            return self.searching_for_game[client_id]
        if client_id in self.sessions:
            session = self.getGameSession(client_id)
            if not session:
                return None
            return session.getClientState(client_id)
        else:
            return None

    def addToSearching(self, client: ClientState):
        if client.client_id not in self.searching_for_game:
            self.searching_for_game[client.client_id] = client

    def isSearching(self, client_id: str):
        return client_id in self.searching_for_game

    def tryToMatch(self):
        if len(self.searching_for_game) < 2:
            return None
        clients_id_matched = list(self.searching_for_game.keys())[:2]
        clients_matched = []
        for client_id in clients_id_matched:
            client = self.searching_for_game.pop(client_id)
            clients_matched.append(client)
        return self.match(clients_matched)

    def match(self, clients: []):
        return self.startGameSession(clients)

    def startGameSession(self, clients):
        session = GameSession()
        for client in clients:
            session.addClient(client)
        for client in clients:
            self.sessions[client.client_id] = session
        return tuple(session.clients.values())

    def getGameSession(self, client_id: str):
        return self.sessions.get(client_id, None)

    def endGameSession(self, client_id: str):
        session = self.getGameSession(client_id)
        for client in session.clients:
            self.sessions.pop(client)

    def clientDisconnected(self, client_id):
        if client_id in self.searching_for_game:
            self.searching_for_game.pop(client_id)
            return True
        else:
            session = self.getGameSession(client_id)
            if session is not None:
                mate = self.getClientMates(client_id)[0]
                mate_state = session.getClientState(mate)
                self.endGameSession(client_id)
                self.addToSearching(mate_state)
                return True
            else:
                return False

    def getClientMates(self, client_id):
        """
        Return other clients info connected to game session
        """
        session = self.getGameSession(client_id)
        if not session:
            return None
        return list(filter(lambda x: x != client_id, session.clients.keys()))
