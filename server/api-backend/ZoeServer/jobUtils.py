import Zoe.work
import Zoe.tasks

from .connections import manager
import os
import glob
import base64
import logging
logger = logging.getLogger(__name__)

# This file contains all things related to processing job files on the server
# those are usually triggered by the server upon commits and alike

def getJobCachePath():
  """Returns the path user for caching job files on the server. Ensures a trailing slash"""
  res = os.environ.get('SERVER_DATA_PATH', None)
  if not res:
    raise Exception('please set the SERVER_DATA_PATH in your .env')
  res = os.path.normpath(os.path.join(res, 'jobCache')) + '/'
  return res

def available():
  """Returns if this module can work properly"""
  try:
    path = getJobCachePath()
    logger.info(f'Job cache path: {path}')
    # TODO: check if its write-able maybe?
    return True
  except Exception as e:
    logger.error(e)
    return False

def jobDeleted(filename, commitInfo):
  """A job got deleted"""
  logger.info(f'Job deleted: {filename}')  
  os.remove(filename)

def jobUpdated(filename, commitInfo):
  """A job got added or modified"""
  logger.info(f'Updated job: {filename}')

async def executeJobOnExecutor(jobFilename, client, commitInfo):
  """Send a new job to be executed on an executor"""
  if not os.path.exists(jobFilename):
    logger.error(f'Job not found: {jobFilename}')
    return False

  fileContent = ''
  with open(jobFilename, mode="r", encoding="utf-8") as f:
    fileContent = f.read()

  logger.info(f'executing job {jobFilename} on client {client["clientid"]} ...')

  await manager.sendToClient(client["clientid"], {
    'type': 'executeFile',
    'data': {
      'filename': jobFilename,
      'commitInfo': commitInfo,
      'filecontent': base64.b64encode(fileContent.encode('utf8'))
    }
  })

def findFittingExecutor(executorTags):
  clients = manager.getClients()
  logger.info(f' *** {len(clients)} clients connected:')
  for clientId, client in clients.items():
    additionalInfo = ''
    if "clientData" in client:
      additionalInfo += ' - ' + client["clientData"]["clientType"]
      if 'name' in client["clientData"]:
        additionalInfo += ' - ' + client["clientData"]["name"]
    logger.info(f' * {client["clientid"]} {additionalInfo}')


  # 1) Match required tags from the job to the executor
  suitableClients = {}
  for clientId, client in clients.items():
    if not "clientData" in client or client['clientData']['clientType'] != 'executor':
      continue
    # fix up the data a bit
    if not 'tags' in client['clientData']:
      client['clientData']['tags'] = []
    allMatched = True
    for eTag in executorTags:
      if not eTag in client['clientData']['tags']:
        allMatched = False
    if allMatched:
      suitableClients[clientId] = client

  # 2) TODO: find a job that is similar
  #matching = {}
  #for clientId, client in clients.items():
  #
  #  rating = 0
  #  for eTag in executorTags:
  #    # rate the tags
  #    if eTag in client['clientData']['tags']:
  #      rating += 1
  #    # the name really counts - in case someone has the funny idea to give their client a tag of someone else's name ;)
  #    if 'name' in client['clientData'] and eTag == client['clientData']['name']:
  #      rating += 100
  #  matching[clientId] = rating
  
  # sort by client id
  sortedMatches = sorted(suitableClients.items(), key=lambda item: item[0], reverse=True) # item[0] = key = clientid

  # TODO:
  # - sort by free execution slots on the machines
  # - sort by affinity to another job that ran on the machines
  # - sort by load on the machines
  # - 

  # For debug logging only:
  logger.info(f'Executor tag matches {executorTags}:')
  for k, v in sortedMatches:
    logger.info(f' * {k}')

  # act upon it
  for clientId, _ in sortedMatches:
    # Return the first match
    return clients[clientId]
  return None

async def commitTrigger(commitInfo):
  """Something got committed, check all the jobs that are active if they want to run :)"""
  logger.info(f'Finding jobs to trigger with this commit: {commitInfo["id"]}')
  jobFiles = glob.glob(getJobCachePath() + '**/*.job.py', recursive=True)
  logger.info(f'Checking {len(jobFiles)} jobs ...')
  for filename in jobFiles:
    jobs = Zoe.work.loadJobsFromFile(filename)
    for job in jobs:
      j = job(os.environ, commitInfo, None)
      j.logger = logger # fix job logging
      res = j.trigger(commitInfo, None)

      # figure out what that means for us
      executorTags = None
      if type(res) == bool and res == True:
        executorTags = []
        # logger.info(f'Job wants to run: {job._NAME} from file {filename} on any executor')
      if type(res) == str:
        executorTags = [res]
      elif type(res) == list:
        executorTags = res
      
      #if not executorTags is None:
      #  logger.info(f'Job wants to run: {job._NAME} from file {filename} on executor with tags: {executorTags}')

      client = findFittingExecutor(executorTags)
      if not client:
        logger.error(f'Unable to find executor with filter {executorTags}')
        continue

      await executeJobOnExecutor(filename, client, commitInfo)