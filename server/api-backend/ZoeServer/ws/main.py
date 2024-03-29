from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState
from ..connections import manager

import json

from .clientLifetimeComm import handleDataLifetime
from .webClientComm import handleDataWeb
from .jobsWsComm import handleDataJobs

from ZoeServer.database import SessionLocal, getDB
from ZoeServer.models import ClientData

from Zoe.utils import decodeMessage

import logging
logger = logging.getLogger(__name__)

def available():
  return True

router = APIRouter(
  #prefix="/ws", # This breaks everything manually add the prefix ...
  tags=["ws"],
  #dependencies=[Depends(get_token_header)],
  responses={404: {"description": "Not found"}},
)

# read the docs please: https://fastapi.tiangolo.com/advanced/websockets/

def addtoDB(clientData: dict, dataRaw: dict):
  # do not add certain events to the DB
  if 'type' in dataRaw and dataRaw['type'] in ['webping', 'register', 'getClients' ]:
    return

  # expect a valid name for the rest
  # no name means that the registration of said node is broken
  nodeName = clientData.get('clientData', {}).get('name', None)
  if not nodeName:
    #logger.error(f"Discarding data: clientData = {clientData}, dataRaw = {dataRaw}")
    return

  # Record it into the DB
  db: SessionLocal = next(getDB())
  db.begin()
  d = ClientData()
  # id = auto increment
  d.nodeName = nodeName
  d.machineUUID = clientData.get('clientData', {}).get('machine_uuid', None)
  
  d.type = dataRaw.get('type', None)
  d.loglevel = dataRaw.get('l', None)
  d.message = dataRaw.get('m', None)
  d.build_id = dataRaw.get('build_id', None)
  d.task_id = dataRaw.get('task_id', None)
  # created_at automatic
  d.extra = json.dumps(dataRaw)
  db.add(d)
  db.flush()
  db.commit()
  res = {
    'id': d.id,
    'nodeName': d.nodeName,
    'machineUUID': d.machineUUID,
    'type': d.type,
    'loglevel': d.loglevel,
    'message': d.message,
    'build_id': d.build_id,
    'task_id': d.task_id,
    'created_at': d.created_at.isoformat(),
    'extra': d.extra,
  }
  return res

async def getEvents():
  db: SessionLocal = next(getDB())
  return db.query(ClientData).order_by(
     ClientData.id.desc()
   ).limit(100).all()

async def sendEventsDB(ws: WebSocket, events):
  res = []
  for e in events:
    res.append({
      'id': e.id,
      'nodeName': e.nodeName,
      'machineUUID': e.machineUUID,
      'type': e.type,
      'loglevel': e.loglevel,
      'message': e.message,
      'build_id': e.build_id,
      'task_id': e.task_id,
      'created_at': e.created_at.isoformat(),
      'extra': e.extra,
    })
  #logger.error(f'DATA: {res}')
  await manager.send(manager.buildMessage('events', res), ws)

eventSubscriptions = {}

async def handleDataMain(ws: WebSocket, clientData: dict, dataRaw: dict):
  """Main callback on receiving data over websocket"""
  
  # let the manager do its work first
  await manager.work()

  # important terms here: 'web' = html websocket client / 'client' = zoe python websocket client
  # there are two communication types: binary and test. Usually the wb clients would be using text only and the zoe clients binary

  # for now, record everything to the database
  eventAdded = addtoDB(clientData, dataRaw)
  if not eventAdded is None:
    eventsAdded = [eventAdded]
    for wss in eventSubscriptions:
      await manager.send(manager.buildMessage('events', eventsAdded), wss)

  dataType = dataRaw['type']
  if dataType == 'subscribeEvents':
    eventSubscriptions[ws] = True # TODO: filters, etc
  elif dataType == 'getEvents':
    await sendEventsDB(ws, await getEvents())

  # then have the various plugins try to deal with the data
  await handleDataLifetime(ws, clientData, dataRaw)
  await handleDataJobs(ws, clientData, dataRaw)
  await handleDataWeb(ws, clientData, dataRaw)



@router.websocket("/ws/")
async def websocket_endpoint(ws: WebSocket):
  """the main entry point for websocket connections"""
  await manager.connect(ws)
  try:
    while ws.client_state == WebSocketState.CONNECTED:
      dataRaw = await ws.receive()
      data = None
      if 'text' in dataRaw:
        data = decodeMessage(dataRaw['text'], False)
      elif 'binary' in dataRaw:
        data = decodeMessage(dataRaw['binary'], True)
      if data:
        await handleDataMain(ws, manager.connections[ws], data)
    manager.disconnect(ws)
  except Exception as ex:
    logger.exception(">>>> EXCEPTION: " + str(ex))
    manager.disconnect(ws)
  except WebSocketDisconnect:
    manager.disconnect(ws)

