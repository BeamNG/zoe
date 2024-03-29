from fastapi import WebSocket

from ..connections import manager
from Zoe.utils import getClientFilesHashes

import logging
logger = logging.getLogger(__name__)

clientFileHashes = getClientFilesHashes()

# this forward is a concept where web clients 'subscribe' to anything another client sends. I.e. listening to logs
forwardClients = { '*': []}



async def handleDataWeb(ws: WebSocket, clientData: dict, dataRaw: dict):
  """Handles communication for client registration, updates, etc"""
  global clientFileHashes, forwardClients

  dataRaw['origin'] = clientData['clientid']

  # forward to sepcific clients?
  if clientData['clientid'] in forwardClients:
    for listenClientId in forwardClients[clientData['clientid']]:
      #print('forward to subscriber: ', forwardClients)
      await manager.sendToClient(listenClientId, dataRaw)

  # catch all clients
  for listenClientId in forwardClients['*']:
    await manager.sendToClient(listenClientId, dataRaw)    

  dataType = dataRaw['type']
  if dataType == 'webping':
    await manager.send(manager.buildMessage('webpong', {}, dataRaw), ws)

  elif dataType == 'chat':
    await manager.broadcast(manager.buildMessage('chat', { 'clientid': clientData['clientid'], 'msg': dataRaw['msg'] }, dataRaw), ws)

  elif dataType == 'getClients':
    await manager.sendClientsList()

  elif dataType == 'subscribe':
    data = dataRaw['data']
    targetClient = data['targetClient']
    if not targetClient in forwardClients:
      forwardClients[targetClient] = []
    else:
      for s in forwardClients[targetClient]:
        if s == clientData['clientid']:
          #await manager.send(manager.buildMessage('subscriptions', forwardClients[targetClient], dataRaw), ws)
          return
    logger.info('client {} will be forwarded to client: {}'.format(targetClient, clientData['clientid']))
    forwardClients[targetClient].append(clientData['clientid'])
    #await manager.send(manager.buildMessage('subscriptions', forwardClients[targetClient], dataRaw), ws)

  elif dataType == 'unsubscribe':
    data = dataRaw['data']
    targetClient = data['targetClient']
    resp = []
    if targetClient in forwardClients:
      for i in range(len(forwardClients[targetClient])):
        s = forwardClients[targetClient][i]
        if s == clientData['clientid']:
          del forwardClients[targetClient][i]
          print('client {} will not anymore forward to client {}'.format(targetClient, clientData['clientid']))
          break
      resp = forwardClients[targetClient]
    #await manager.send(manager.buildMessage('subscriptions', forwardClients[targetClient], dataRaw), ws)

  # TODO: FIXME
  #elif dataType == 'subscriptions':
  #  resp = []
  #  if targetClient in forwardClients:
  #    resp = forwardClients[targetClient]
  #  await manager.send(manager.buildMessage('subscriptions', resp, dataRaw), ws)


  #elif dataType == 'log':  # used in: ?
  #  pass

  elif dataType == 'updateAllClients':
    #data = dataRaw['data'] # backward compatibility for now ...
    clientFileHashes = getClientFilesHashes()
    #logger.error('server hashes: {}'.format(clientFileHashes))
    await manager.broadcast(manager.buildMessage('fileHashes', clientFileHashes, dataRaw))

  elif dataType == 'requestFilesList':
    clientFileHashes = getClientFilesHashes()
    await manager.send(manager.buildMessage('fileHashes', clientFileHashes, dataRaw), ws)
