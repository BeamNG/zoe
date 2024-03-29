from fastapi import WebSocket
from ..connections import manager

import logging
logger = logging.getLogger(__name__)

async def handleDataJobs(ws: WebSocket, clientData: dict, dataRaw: dict):
  """Handles communication anything job related"""

  dataType = dataRaw['type']
  if dataType == 'executeFile':  # used in: web > clients
    # simply forward for now
    await manager.sendToClient(dataRaw['data']['targetClient'], dataRaw)
  #else:
  #  logger.error('unknown data: ' + str(dataRaw))
