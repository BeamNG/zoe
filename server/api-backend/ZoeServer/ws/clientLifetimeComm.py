import os
from fastapi import WebSocket
from ..connections import manager

from Zoe.utils import hashFileSHA1, getClientFilesHashes, getClientInstallationPath

import logging
logger = logging.getLogger(__name__)

clientFileHashes = getClientFilesHashes()

async def handleDataLifetime(ws: WebSocket, clientData: dict, dataRaw: dict):
  """Handles communication for client registration, updates, etc"""
  global clientFileHashes

  dataType = dataRaw['type']
  if dataType == 'register':  # used in: clients, web
    data = dataRaw
    if 'data' in dataRaw:
      data = dataRaw['data']
    
    # clean up the data a bit ...
    data = dict(data) # create a copy
    data.pop('type', None)
    data.pop('origin', None)
    clientData['clientData'] = data

    # set binary capable flag
    if 'binaryCapable' in data and data['binaryCapable'] == True:
      clientData['binaryCapable'] = True

    # send hashes to the client so it could update automatically after registering
    clientFileHashes = getClientFilesHashes()
    await manager.send(manager.buildMessage('fileHashes', clientFileHashes, dataRaw), ws)
    await manager.sendClientsList()

  elif dataType == 'ping':  # used in: clients
    clientData['clientStats'] = dataRaw['data']
    await manager.sendClientsList()

  elif dataType == 'requestFiles':  # used in: clients, web
    data = dataRaw['data'] # backward compatibility for now ...
    requestedFiles = data
    #print('client {} requested an update of the following files: {}'.format(clientData['clientid'], requestedFiles))
    fileData = {}
    sentHashes = {}
    for filename in requestedFiles:
      filenameDisk = os.path.normpath(os.path.join(getClientInstallationPath(), filename.replace('..', '')))
      if os.path.isfile(filenameDisk):
        fileHash = hashFileSHA1(filenameDisk)
        if fileHash == clientFileHashes[filename]:
          with open(filenameDisk, 'rb') as file:
            fileData[filename] = file.read()
          sentHashes[filename] = clientFileHashes[filename]
        else:
          logger.error('Error: hash table out of date? {} / {} {}'.format(filename, fileHash, clientFileHashes[filename]))
      else:
        logger.error('File not existing: {}'.format(filenameDisk))
    await manager.send(manager.buildMessage('updateData', { 'fileData': fileData, 'fileHashes': sentHashes }, dataRaw), ws)
