import zoe_ci
import os
import time
import inspect
import threading
import logging
import logging
import json
import base64
import importlib.util
from datetime import datetime

from zoe_ci.utils import decodeMessage, hashPath, restartScript, hashFileSHA1, ZoeException

from zoe_ci.gpuInfo import GpuInfo

logger = logging.getLogger('zoe')

parentPath = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
MAKE_FILE_BACKUPS = False

# instantiate the gpu class
gpu_client = GpuInfo()

try:
  if gpu_client.getGpuCount() > 0:
    for gpu in gpu_client.getGpuInfo():
      gpu_name = gpu[0]
      gpu_free_memory = gpu[1]
      gpu_load = gpu[2]
  else:
    gpu_name = None
    gpu_free_memory = None
    gpu_load = None
except ZoeException:
  logger.exception("An error occurred while getting GPU info")


class Runtime():
  buildId: str = None # the build number of the current execution

class Job():
  def __init__(self, env, commitInfo, executorInfo):
    self.env = env
    self.commitInfo = commitInfo
    self.executorInfo = executorInfo
    self.logger = logging.getLogger(self.__class__.__name__)

  def setup(self, commitInfo, executorInfo):
    pass

  def run(self, commitInfo, executorInfo):
    pass

  def teardown(self, commitInfo, executorInfo):
    pass

  def _getAndIncreaseBuildNumber(self):
    jsonFilename = os.path.join(os.environ['WORKSPACE'], 'config.json')
    data = None
    if os.path.exists(jsonFilename):
      try:
        with open(jsonFilename, 'r') as f:
          data = json.load(f)
      except:
        pass
    if data is None:
      data = { 'build_number': 0 }
    data['zoe_version'] = zoe_ci.__version__

    data['build_number'] = int(data['build_number']) + 1
    data['last_build'] = datetime.now().isoformat()

    os.makedirs(os.environ['WORKSPACE'], exist_ok = True)
    with open(jsonFilename, 'w') as f:
      json.dump(data, f, sort_keys=True, indent=2)

    return data['build_number']

  def _execute(self):
    if not os.environ.get('WORKSPACE', None):
      workspace_root = os.environ.get('WORKSPACE_ROOT', 'workspace')
      if workspace_root:
        if not os.path.isabs(workspace_root):
          workspace_root = os.path.join(parentPath, workspace_root)

      os.environ['WORKSPACE'] = os.path.join(workspace_root, self.__class__.__name__)

    os.environ['WORKSPACE'] = os.path.normpath(os.environ['WORKSPACE'])

    # TODO: implement more env variables: BUILD_NUMBER, NODE_NAME, JOB_NAME, BUILD_TAG, EXECUTOR_NUMBER, SVN_REVISION, GIT_COMMIT, GIT_URL, GIT_BRANCH

    # Figure out build number per job:
    Runtime.buildId = self._getAndIncreaseBuildNumber()
    os.environ['BUILD_NUMBER'] = str(Runtime.buildId)

    os.makedirs(os.environ['WORKSPACE'], exist_ok=True)
    os.chdir(os.environ['WORKSPACE'])

    with zoe_ci.tasks.GenericTask(self.__class__.__name__):
      self.setup(self.commitInfo, self.executorInfo)
      self.run(self.commitInfo, self.executorInfo)
      self.teardown(self.commitInfo, self.executorInfo)

def loadJobsFromModule(module):
  jobs = []
  for name, cls in inspect.getmembers(module, inspect.isclass):
    if issubclass(cls, zoe_ci.work.Job):
      cls._NAME = name
      jobs.append(cls)
  if len(jobs) == 0:
    logger.error('No jobs found')
    return []
  return jobs

def loadJobsFromFile(filename):
  if not os.path.isfile(filename):
    logger.error("Job file not readable: {}".format(filename))
    return []

  try:
    spec = importlib.util.spec_from_file_location('Job', filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return loadJobsFromModule(module)
  except Exception as e:
    logger.error("Unable to load job file {}: {}".format(filename, e))
    return []

def loadJobFromMemory(filename, fileContent):
  try:
    spec = importlib.util.spec_from_loader('Job', loader=None)
    module = importlib.util.module_from_spec(spec)
    exec(fileContent, module.__dict__)
    return loadJobsFromModule(module)
    #sys.modules['Job'] = module
  except Exception as e:
    logger.error("Unable to load job file {}: {}".format(filename, e))
    return []
    
class Executor():
  def __init__(self, env):
    self.env = env
    self.dataReady = threading.Condition()
    self.pingTime = 60
    self.lastPingTime = time.process_time() - self.pingTime

  def _getExecutorInfo(self):
    import platform
    info = {
      'clientType': 'executor',
      'name': platform.node().lower(),
      'ZoeVersion': zoe_ci.__version__,
      'machine_uuid': self.env.get('machine_uuid', None),
      'binaryCapable': True, # important to allow binary websocket communication
      'platform': {
        'arch': platform.architecture(),
        'machine':  platform.machine().lower(),
        'node':  platform.node().lower(),
        'platform':  platform.platform(),
        'processor':  platform.processor(),
        'python_build':  platform.python_build(),
        'python_compiler':  platform.python_compiler(),
        'python_branch':  platform.python_branch(),
        'python_implementation':  platform.python_implementation(),
        'python_revision':  platform.python_revision(),
        'python_version':  platform.python_version(),
        'python_version_tuple':  platform.python_version_tuple(),
        'release':  str(platform.release()).lower(),
        'system':  platform.system(),
        'version':  platform.version(),
        'uname':  platform.uname(),
        'gpu_name': gpu_name if gpu_name else None,
        'gpu_free_memory': gpu_free_memory if gpu_free_memory else None,
        'gpu_load': gpu_load if gpu_load else None,
      },
      # tags are a way of defining features for tests to select where to run on
      # i.e. a test can say it wants to run on: ['windows', 'amd', 'max spec']
      # or on a specific node name for example
      'tags': []
    }

    # add some tags :)
    # tags are always lower-case please
    info['tags'].append(platform.system()) # windows / linux
    info['tags'].append(f"{platform.system()}{str(platform.release())}") # windows10, linux5.15.0-53-generic
    info['tags'].append(platform.architecture()[0]) # 64bit
    info['tags'].append(platform.node()) # DESKTOP-XXXX, testinglinux
    info['tags'].append(platform.machine()) # machine type: AMD64, x86_64
    info['tags'].append(gpu_name)
    info['tags'].append(gpu_load)
    info['tags'].append(gpu_free_memory)
    # TODO:
    # - minspec, midspec, max spec
    # - can this windows build machine compile for consoles? Is a console attached for debugging or testing?

    # ensure everything is lower case ;) 
    info['tags'] = [str(x).lower() for x in info['tags']]

    info['autoupdate'] = 'autoupdate' in self.env and self.env['autoupdate']
    if platform.system() == 'Windows':
      info['platform']['win32_is_iot'] = platform.win32_is_iot()

      #for v in ['COMPUTERNAME', 'TIME', 'DATE', 'USERNAME', 'NUMBER_OF_PROCESSORS', 'APPDATA']:
      #  data[v] = zoe_ci.utils.getWindowsShellVariable(v)

    elif platform.system() == 'Darwin':
      info['platform']['mac_ver'] = platform.mac_ver()
    elif platform.system() == 'Linux':
      info['platform']['libc_ver'] = platform.libc_ver()
    return info
  
  def setup(self):
    from zoe_ci.serverConnection import createComms
    self.executorInfo = self._getExecutorInfo()
    self.comm = None
    if not 'localMode' in self.env:
      self.comm = createComms(self, self.env, self.executorInfo)

  def teardown(self):
    """
    Stop the thread
    """
    if self.comm:
      self.comm.stopThread()

  def handleMessage(self, msgRaw):
    msg = decodeMessage(msgRaw[0], msgRaw[1] == 2)
    if type(msg) != dict or 'type' not in msg:
      logger.error(f'Invalid message received: {msg}')
      return

    if msg['type'] == 'fileHashes':
      self._checkUpdate(msg['data'])

    elif msg['type'] == 'executeFile':
      filename = msg['data']['filename']
      filecontent = base64.b64decode(msg['data']['filecontent']).decode()
      try:
        commitInfo = msg['data']['commitInfo']
      except KeyError:
        commitInfo = None
      self._executeJobs(loadJobFromMemory(filename, filecontent), commitInfo)

    elif msg['type'] == 'updateData':
      if not self.env['autoupdate']:
        logger.info('Auto update rejected')
        return

      logger.info('  + AUTO-UPDATE: Downloading files ...')
      if not 'data' in msg or not 'fileData' in msg['data'] or not 'fileHashes' in msg['data']:
        logger.error('malformed update data: ' + str(msg))
        return
      try:
        fileData = msg['data']['fileData']
        fileHashes = msg['data']['fileHashes']
        if len(fileData) == 0:
          logger.info('Auto update empty')
          return

        for filename in fileData:
          filenameDisk = os.path.normpath(os.path.join(parentPath, filename.replace('..', '')))
          os.makedirs(os.path.dirname(filenameDisk), exist_ok=True)
          if MAKE_FILE_BACKUPS and os.path.isfile(filenameDisk):
            oldFilename = filenameDisk + '.old'
            if os.path.isfile(oldFilename):
              os.unlink(oldFilename)
            os.rename(filenameDisk, oldFilename)
            #print("OLD FILE HASH: ", hashFileSHA1(oldFilename))
          with open(filenameDisk, 'wb') as file:
            file.write(fileData[filename])
          fileHash = hashFileSHA1(filenameDisk)
          if fileHash != fileHashes[filename]:
            logger.error('  * {} - incorrect hash: {} {}'.format(filename, fileHash, fileHashes[filename]))
            logger.error('  + AUTO-UPDATE: ABORTED')
            return
          logger.info('  * {} - OK'.format(filename))
          #logger.info('   * successfully downloaded and verified file {} ({}) with hash {}'.format(filename, filenameDisk, fileHash))
        logger.info('  + AUTO-UPDATE: DONE - restarting now')
        self.teardown()
        restartScript()
        #sys.exit(0)
      except Exception as ex:
        logger.exception('Exception on auto update: ' + str(ex))

    #else:
    #  print("got unknown message: ", msg)

  def _sendPingIfNeeded(self):
    import psutil
    if time.process_time() - self.lastPingTime < self.pingTime:
      return
    self.lastPingTime = time.process_time()
    data = {
      'memory_virtual': psutil.virtual_memory()._asdict(),
      'memory_swap': psutil.swap_memory()._asdict(),
      'cpu_freq': psutil.cpu_freq()._asdict(),
      'cpu_times': psutil.cpu_times()._asdict(),
      'cpu_loadavg': psutil.getloadavg(),
      #'netcounters': psutil.net_io_counters(pernic=True),
      #'sensors_temperatures': psutil.sensors_temperatures(),
      #'sensors_fans': psutil.sensors_fans(),
      #'sensors_battery': psutil.sensors_battery(),
    }
    self.comm.send(json.dumps({'type': 'ping', 'data': data}))

  def serveForever(self):
    self.dataReady.acquire()
    self.setup()
    while True:
      self._sendPingIfNeeded()
      if self.dataReady.wait(self.pingTime):
        while not self.comm.recvQueue.empty():
          self.handleMessage(self.comm.recvQueue.get())
 
  def _executeJobs(self, jobs, commitInfo):
    if len(jobs) == 0:
      logger.error('no jobs found, exiting')
      return 1
    for job in jobs:
      j = job(self.env, commitInfo, self.executorInfo)
      j._execute()

  def executeLocalJobs(self, jobfilename, commitInfo=None):
    self.setup()
    self._executeJobs(loadJobsFromFile(jobfilename), commitInfo)
    self.teardown()

  def _checkUpdate(self, serverHashes):
    if not self.comm or not self.env['autoupdate']:
      return

    localHashes = hashPath(parentPath)

    localFiles = localHashes.keys()
    serverFiles = serverHashes.keys()


    outdatedFiles = []
    # find modified / deleted files
    for f in localFiles:
      if f in serverFiles and localHashes[f] != serverHashes[f]:
        # modified
        #logger.info(' * {} M'.format(f))
        outdatedFiles.append(f)
      #elif not f in serverFiles:
        #logger.info(' * {} D'.format(f))
        #print('local file not present on server: ' + str(f))

    # find new files
    for f in serverFiles:
      if not f in localFiles:
        #logger.info(' * {} A'.format(f))
        outdatedFiles.append(f)

    if len(outdatedFiles) == 0:
      # no updates needed, all up to date
      #logger.info(" + AUTO-UPDATE: SYNCED")
      return

    logger.info(' + AUTO-UPDATE: Updating {} files ...'.format(len(outdatedFiles)))
    self.comm.send({ 'type': 'requestFiles', 'data': outdatedFiles })
