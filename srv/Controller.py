import logging
import attr
from common.crypto_utils import loadPublicKey, fromBase64, verify, getMD5
from faker import Faker
from srv.SessionMgr import ClientState
from common.utils import makeErrorResponse


@attr.s
class Controller:
    db = attr.ib(default=None)
    session_mgr = attr.ib(default=None)

    def playerRegister(self, query):
        try:
            key_str = query.get("key", None)
            key_data = fromBase64(key_str)
            key = loadPublicKey(key_data)
            if key is None:
                logging.info("Invalid key")
                return makeErrorResponse("Invalid key")
            signature = query.get("signature", None)
            signature_data = fromBase64(signature)
            if signature_data is None:
                logging.error("No signature")
                return makeErrorResponse("No signature")
            if not verify(key_data, signature_data, key):
                logging.error("Signature doesnt math")
                return makeErrorResponse("Signature doesnt match")
        except Exception as e:
            return makeErrorResponse(str(e))
        client_id = getMD5(key_data)
        user_info = self.db.getUserInfo(client_id)
        if user_info is None:
            logging.info("generating user name")
            name = Faker("uk_UA").name().replace(" ", "_")
            self.db.storeUserInfo(client_id, {"name": name, "key": key_str})
        else:
            logging.info("user found")
            name = user_info["name"]
        return {"result": "ok", "id": client_id, "name": name}

    async def playerDisconnected(self, client_id):
        if self.db is not None:
            user_info = self.db.getUserInfo(client_id)
            logging.info(f'Player {user_info["name"]} disconnected')
        if self.session_mgr is not None:
            self.session_mgr.clientDisconnected(client_id)
            await self.makeMatch()
        return makeErrorResponse()

    async def makeMatch(self):
        clients_matched = self.session_mgr.tryToMatch()
        if clients_matched:
            client1, client2 = clients_matched
            await client1.ws_connection.send_str(
                f"hi, session found with "
                f"{client2.client_info['name']}")
            await client2.ws_connection.send_str(
                f"hi, session found with "
                f"{client1.client_info['name']}")

    async def sessionStarted(self, client_id, ws):
        client_info = self.db.getUserInfo(client_id)

        clientState = ClientState(client_id=client_id,
                                  ws_connection=ws,
                                  client_info=client_info)
        self.session_mgr.addToSearching(clientState)
        await self.makeMatch()

    async def messageReceived(self, msg, client_id):
        session = self.session_mgr.getGameSession(client_id)
        if not session:
            client_state = self.session_mgr.findClientState(client_id)
            await client_state.ws_connection.send_str("Session not found")
            return
        client = self.db.getUserInfo(client_id)
        mate = self.session_mgr.getClientMates(client_id)[0]
        mate_state = session.getClientState(mate)
        logging.info(f"{msg}")
        await mate_state.ws_connection.send_str(
            f"{client['name']}: {msg.data}")

    def getInfo(self):
        return repr(self.session_mgr)

    def playerMsgReceived(self, key, message):
        return {}
