import os

from zoe_ci.utils import *
from zoe_ci.tasks import *

import logging
logger = logging.getLogger('git')


def logGitVersion():
  """For debugging purposes, logs the git version"""
  try:
    git_version = exec('git --version', optional=True)[1][0]
    logger.debug('Found {git_version:}'.format(git_version = git_version), extra = {'git_version': git_version})
  except:
    logger.warn('Unable to get git version')

def gitSync(vcs: VCS, task: GenericTask = None):
  with GenericTask("git sync"):
    execCtx = {'vcs': vcs, 'workingDirectory': vcs.outPath}
    res = False
    try:
      if not exec_available('git') or exec_available('git-lfs'):
        raise ZoeException('git executable not usable')
    except ZoeException as e:
      logger.exception(e)

    logGitVersion()

    os.chdir(os.environ['WORKSPACE'])

    if os.path.exists(vcs.outPath): # relative path ok, we are always by default in the workspace path
      for i in range(1, 5):
        if execBlock(f"""
  git fetch origin
  git reset --hard origin/{vcs.branch:}
  git submodule foreach "git submodule sync"
  git submodule update --init --recursive --force
  git lfs pull
  git clean -fdx
  git submodule foreach --recursive git clean -fdx
  """, **execCtx):
          res = True
          break
    else:
      res = exec('git clone -j 8 -b {vcs.branch:} {vcs.url:} .', **execCtx) # . because we are already in the output path

  return res