import argparse
import logging
import sys
import os
import json

depsPath = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, depsPath)

os.environ["PYTHONUNBUFFERED"] = "1"

import zoe_ci
from zoe_ci.utils import installSignalHandler
import zoe_ci.work

logger = None

def setupLogging():
  global logger
  stream_handler = logging.StreamHandler()
  stream_handler.setLevel(logging.INFO)
  logging.basicConfig(level=logging.DEBUG, format='%(asctime)s | %(levelname)s | %(name)s | %(message)s', handlers=[
    #logging.FileHandler("my_log.log", mode='w'),
    stream_handler
  ])
  logger = logging.getLogger('zoe')

  if not os.environ.get('RUNNING_AS_WINDOWS_SERVICE', None) and not os.environ.get('NO_COLORLOG', None):
    # only use color logs if not running as windows service
    try:
      import coloredlogs
      coloredlogs.install(logging.INFO, fmt='%(asctime)s | %(levelname)s | %(name)s | %(message)s')
    except ImportError:
      pass


def loadDotEnv():
  try:
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv(filename=".env.default"))
    load_dotenv(find_dotenv(filename=".env"))
  except Exception as e:
    logger.exception(e)

def loadLocalConfig():
  try:
    from uuid import uuid4
    from appdirs import user_data_dir
    appConfigPath = user_data_dir('zoe_ci', 'BeamNG')
    jsonFilename = os.path.join(appConfigPath, 'config.json')
    data = None
    if os.path.exists(jsonFilename):
      try:
        with open(jsonFilename, 'r') as f:
          data = json.load(f)
      except:
        pass
    if data is None:
      uuid = uuid4().hex
      logger.info('Generated new UUID for this machine: {}'.format(uuid))
      data = { 'machine_uuid': uuid }
    data['zoe_version'] = zoe_ci.__version__
    os.makedirs(appConfigPath, exist_ok = True)
    with open(jsonFilename, 'w') as f:
      json.dump(data, f, sort_keys=True, indent=2)
    return data
  except Exception as e:
    logger.exception(e)
    return {}


def zoeMain():
  setupLogging()
  logger.info(f"===== Welcome to zoe_ci v{zoe_ci.__version__} =====")
  loadDotEnv()
  parser = argparse.ArgumentParser(prog='zoe', description='The zoe_ci client and execution program suit')
  # mode flags
  parser.add_argument("-j", "--jobfile", help="job filename to process", default=None, nargs='?')

  # boolean flags
  parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
  parser.add_argument("-q", "--quiet", help="decrease output verbosity", action="store_true")
  parser.add_argument("-l", "--local", help="offline mode. No communication with the server.", action="store_true")
  parser.add_argument("-u", "--autoupdate", help="Enable automatic updates", action="store_true")

  args = parser.parse_args()

  if args.verbose:
    logger.setLevel(logging.DEBUG)
  if args.quiet:
    logger.setLevel(logging.ERROR)

  env = loadLocalConfig()
  env['autoupdate'] = args.autoupdate
  if args.local:
    env['localMode'] = True
    if not args.jobfile:
      logger.error('Local mode is not available when running as executor')
      return 1

  ex = zoe_ci.work.Executor(env)
  if args.jobfile:
    return ex.executeLocalJobs(args.jobfile.strip())
  else:
    installSignalHandler()
    return ex.serveForever()


if __name__ == "__main__":
  sys.exit(zoeMain())
