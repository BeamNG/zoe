import logging
import time
from uuid import uuid4

from fastapi import WebSocket
from starlette.websockets import WebSocketState

from typing import Union, Optional

import Zoe
from Zoe.utils import encodeMessageBinary, encodeMessageText


logger = logging.getLogger(__name__)

def available():
  return True
  
class ConnectionManager:
  """Manages all client connections"""

  def __init__(self):
    self.connections: dict[WebSocket] = {}

    # some temp buffers to work on on the next 'work' call
    self._clientsDisconnected: list[WebSocket] = []
    self._clientsConnected: list[WebSocket] = []

  async def connect(self, ws: WebSocket):
    await ws.accept()
    cid = uuid4().hex
    self.connections[ws] = { 'clientid': cid }
    self._clientsConnected.append([ws, cid])

  def disconnect(self, ws: WebSocket):
    cid = -1
    if ws in self.connections:
      cid = self.connections[ws].get('clientid', -1)
      del self.connections[ws]
    self._clientsDisconnected.append([ws, cid])

  def getClients(self):
    # exchange the ws socket in the key with the client id as the ws is meaningless for any API user
    return dict((self.connections[wsIdx]['clientid'], value) for (wsIdx, value) in self.connections.items())

  async def send(self, msgRaw: Union[int, str, dict], ws: WebSocket):
    if ws.client_state != WebSocketState.CONNECTED:
      #logger.error('trying to send on disconnected socket')
      #print(" # clients connected: " + str(len(self.connections)))
      return
    try:
      if ws in self.connections and 'binaryCapable' in self.connections[ws]:
        await ws.send_bytes(encodeMessageBinary(msgRaw))
      else:
        await ws.send_text(encodeMessageText(msgRaw))
    except Exception as ex:
      logger.critical(ex, exc_info=True)
      logger.critical("message: " + str(msgRaw))

  async def broadcast(self, msgRaw: Union[int, str, dict], exceptWS: Optional[WebSocket] = None):
    for ws in list(self.connections.keys()):
      if ws == exceptWS:
        continue
      await self.send(msgRaw, ws)

  async def sendClientsList(self):
    clients = []
    for ws in list(self.connections.keys()):
      if 'clientData' in self.connections[ws]:
        if self.connections[ws]['clientData'].get('clientType', '') == 'executor':
          clients.append(self.connections[ws])
    await self.broadcast(self.buildMessage('clients', clients))

  async def sendToClient(self, clientId, data):
    for ws in list(self.connections.keys()):
      if self.connections[ws]['clientid'] == clientId:
        await self.send(data, ws)
        return
    logger.error('client for sending not found: {}'.format(clientId))

  def buildMessage(self, type: str, data: Union[int, str, dict], query: dict = None):
    # pprint(data)
    resp = { "type": type, "data": data }
    if query:
      resp["timestamp"] = time.time()
      if "state" in query:
        resp["state"] = query["state"]  # this should probably be limited to string type and by length
    return resp

  async def work(self):
    changed = len(self._clientsConnected) > 0 or len(self._clientsDisconnected) > 0
    for ws, cid in self._clientsConnected:
      await self.send(self.buildMessage('clientInfo', { 'clientid': cid, 'ZoeServerVersion': Zoe.__version__ }), ws)
    self._clientsConnected = []
    for ws, cid in self._clientsDisconnected:
      await self.send(self.buildMessage('clientInfo', { 'clientid': cid, 'ZoeServerVersion': Zoe.__version__ }), ws)
    self._clientsDisconnected = []
    if changed:
      await self.sendClientsList()

# the global instance for everyone to use
manager = ConnectionManager()
