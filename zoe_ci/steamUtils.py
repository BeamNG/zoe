import os

from zoe_ci.utils import *
import zoe_ci.tasks

import logging
logger = logging.getLogger('steamcmd')

steamcmd_exe = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'misc', 'steamcmd', 'steamcmd.exe'))

def steamSync(vcs: VCS):
  with zoe_ci.tasks.GenericTask("steam sync"):
    res = False

    os.chdir(os.path.join(os.environ['WORKSPACE'], vcs.outPath))

    with open('steamcmds.txt', 'w') as f:
      f.write("""
  // DO NOT EDIT, AUTOMATICALLY GENERATED
  //
  @ShutdownOnFailedCommand 1
  @NoPromptForPassword 1
  force_install_dir .
  //login {STEAM_USERNAME:} {STEAM_PASSWORD:}
  login anonymous
  app_update 740 validate
  quit
  """)

    res,_ = exec('{steamcmd_exe:} +runscript steamcmds.txt'.format(steamcmd_exe = steamcmd_exe))

    os.unlink('steamcmds.txt')
    return res