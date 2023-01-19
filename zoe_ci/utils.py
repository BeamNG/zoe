import os
import shutil
import hashlib
import glob
import json
import msgpack
import logging
import sys

import zoe_ci.tasks

logger = logging.getLogger('utils')
_startup_cwd = os.getcwd()


class ZoeException(BaseException):
  pass

def recursive_delete(path: str) -> None:
  def onerror(func, path, exc_info):
    import stat
    if not os.access(path, os.W_OK):
      os.chmod(path, stat.S_IWUSR)
      func(path)
  shutil.rmtree(path, onerror=onerror)

def installSignalHandler() -> None:
  import signal
  import sys
  def signal_handler(signal, frame):
      sys.exit(0)
  signal.signal(signal.SIGINT, signal_handler)

def restartScript() -> None:
  args = sys.argv[:]
  args.insert(0, sys.executable)
  if sys.platform == 'win32':
    args = ['"{}"'.format(arg) for arg in args]

  logger.info('restarting {}'.format(' '.join(args)))
  sys.stdout.flush()
  sys.stderr.flush()
  #os.fsync()
  os.chdir(_startup_cwd)

  # this is a hack for windows + execv:
  if os.environ.get('RUNNING_AS_WINDOWS_SERVICE', None):
    # restart using the service to not confuse windows
    # if we do not do this, you'll end up with two processes running
    sys.exit(0)

  os.execv(sys.executable, args)

def hashFileSHA1(filename):
  BUF_SIZE = 65536 # 64kb chunks
  sha1 = hashlib.sha1()
  with open(filename, 'rb') as file:
    while True:
      data = file.read(BUF_SIZE)
      if not data:
        break
      sha1.update(data)
  return sha1.hexdigest()

def encodeMessageBinary(data):
    return msgpack.packb(data, use_bin_type=True)

def encodeMessageText(data):
  return json.dumps(data, default=lambda o: o.decode("utf-8") or '<not serializable>')

def decodeMessage(data, isBinary):
  """can decode messagepack and json"""
  if isBinary:
    return msgpack.unpackb(data)
  else:
    try:
      return json.loads(data)
    except json.JSONDecodeError as jex:
      logger.exception(jex)


def hashPath(path):
  filenames = glob.glob(os.path.join(path, '**'), recursive = True)
  fileHashes = {}
  for filename in filenames:
    (rootPath, fileExt) = os.path.splitext(filename)
    if not os.path.isfile(filename) or fileExt.lower() == '.pyc':
      continue
    fileHashes[os.path.relpath(filename, path).replace('\\', '/')] = hashFileSHA1(filename)
  return fileHashes

# TODO: kill this thing and just have a SVN / GIT class
class VCS:
  type: str = 'svn'
  url: str = 'http://svn/game/trunk'
  branch: str = 'main' # used for git
  targetRevision: str = 'HEAD'
  outPath: str = 'trunk'
  username: str = os.environ.get('SVN_USER')
  password: str = os.environ.get('SVN_PASS')

  def __init__(self, **kwargs):
    self.__dict__.update(kwargs)

  def sync(self):
    if self.type == 'svn':
      return svnSync(self)
    elif self.type == 'git':
      return gitSync(self)
    else:
      logger.error('Unknown self: ' + str(self.type))

def exec_available(exeName: str):
  return shutil.which(exeName) is not None


def execBlock(cmdBlock, **kwargs):
  res = True
  cmdLines = cmdBlock.strip().split('\n')
  for cmd in cmdLines:
    cmd = cmd.strip()
    if len(cmd) == 0 or cmd[0] == '#':
      continue
    res = res and zoe_ci.tasks.ShellTask(cmd, **kwargs).run()
  return res

def exec(*args, **kwargs):
  return zoe_ci.tasks.ShellTask(*args, **kwargs).run()

def human_readable_size(size, decimal_places = 2):
  for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
    if size < 1000.0 or unit == 'PB':
      break
    size /= 1000.0
  return f"{size:.{decimal_places}f} {unit}"

def getWindowsShellVariable(varName):
  return ''.join(zoe_ci.tasks.ShellTask('echo %{}%'.format(varName), shell=True).run()[1])

def getUnixShellVariable(varName):
  return ''.join(zoe_ci.tasks.ShellTask('echo ${}'.format(varName), shell=True).run()[1])

def runCommandSimple(cmd):
  return ''.join(zoe_ci.tasks.ShellTask(cmd, shell=True).run()[1])

from zoe_ci.svnUtils import svnSync
from zoe_ci.gitUtils import gitSync


def getClientInstallationPath():
  return os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

def getClientFilesHashes():
  """we hash the client files to allow comparison / auto-updating"""
  clientFileHashesRaw = hashPath(getClientInstallationPath())
  res = {}
  for filename in clientFileHashesRaw:
    if not filename.startswith('workspace/'):
      res[filename] = clientFileHashesRaw[filename]
  #logger.debug(f'Tracking {len(res)} client files...')
  return res