import os
import re
import time

from zoe_ci.utils import *
from zoe_ci.tasks import *
import zoe_ci.tasks

import logging
logger = logging.getLogger('svn')

# re for svn list
svn_list_re = re.compile(r'^([0-9]+)[ ]+([^ ]+)[ ]+(?:([0-9]+)|)[ ]+(?:[a-zA-Z]+ [0-9]+[ ]+[0-9:]+|) (.+)$')
# re for svn checkout/update
svn_update_re = re.compile(r'^([^ ]+)[ ]+(.+)$')

class _ProgressReporterSimple:
  """helper logging class"""
  def progress(self, line):
    extra = {
      'type': 'task_progress',
    }
    if hasattr(self, 'shellTask'):
      self.shellTask._fillLoggerTaskData(extra)
    logger.info(line.strip(), extra = extra)

  def finalReport(self):
    pass
    #self.progress("task done")

class _SVNListOutputProcessor:
  """helper class for svn list"""
  def __init__(self):
    self.svn_files = {}
    self.total_bytes = 0
    self.lastTime = time.time()

  def progress(self, line):
    extra = {
      'type': 'task_progress',
      'svn_state': 'svn_list',
      'found_files': len(self.svn_files),
      'total_bytes': self.total_bytes,
    }
    line = line.strip()
    res = svn_list_re.findall(line)
    if res:
      res = list(res[0])
      res[0] = int(res[0])
      if len(res) > 2 and res[2].isdigit():
        res[2] = int(res[2])
        self.total_bytes += res[2]
        dt = time.time() - self.lastTime
        if dt > 1:
          self.lastTime = time.time()
          if hasattr(self, 'shellTask'):
            self.shellTask._fillLoggerTaskData(extra)

          logger.info("Found {: >6} ({: >9}) files so far ...".format(
            len(self.svn_files),
            human_readable_size(self.total_bytes)
          ), extra = extra)
      else:
        res[2] = 0
      self.svn_files[res[-1].rstrip('/')] = res
    else:
      logger.info(line, extra = extra)

  def finalReport(self):
    pass
    #self.progress("task done")

  def getResults(self):
    return self.svn_files, self.total_bytes

class _SVNCheckoutOutputProcessor:
  """helper class for svn checkout"""
  def __init__(self, svn_files, total_size, **execCtx):
    self.svn_files = svn_files
    self.filecount = len(svn_files)
    self.fileCounter = 0
    self.lastTime = time.time() - 8
    self.bytesDownloadedTemp = 0
    self.bytesDownloaded = 0
    self.bytesLeft = total_size
    self.bytesTotal = total_size
    self.startTime = time.time()

  def _formatSeconds(self, seconds):
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return '{:d}:{:02d}:{:02d}'.format(h, m, s)

  def finalReport(self):
    if self.fileCounter > 0:
      timePassed = time.time() - self.startTime
      speed = self.bytesDownloaded / timePassed
      extra = {
        'type': 'task_progress',
        'svn_state': 'checkout_done',
        'filesDone': self.fileCounter,
        'bytesTotal': self.bytesTotal,
        'dlSpeed': speed,
        'timePassed': timePassed
      }
      if hasattr(self, 'shellTask'):
        self.shellTask._fillLoggerTaskData(extra)
      logger.info('Done. Downloaded {filesDone:} files ({bytesTotal:}) at {dlSpeed:}/s in {t:}'.format(
        filesDone = self.fileCounter,
        bytesTotal = human_readable_size(self.bytesTotal),
        dlSpeed = human_readable_size(speed),
        t = self._formatSeconds(timePassed)
      ), extra = extra)

  def progress(self, line):
    line = line.strip()
    self.fileCounter += 1
    res = svn_update_re.findall(line)
    speed = 0
    extra = {
      'type': 'task_progress',
    }
    if hasattr(self, 'shellTask'):
      self.shellTask._fillLoggerTaskData(extra)
    if res:
      res = res[0]
      filename = res[1].replace('\\', '/').strip()
      if filename in self.svn_files:
        fileSize = self.svn_files[filename][2]
        self.bytesDownloadedTemp += fileSize
        self.bytesDownloaded += fileSize
        self.bytesLeft -= fileSize
    else:
      logger.info(line, extra = extra)

    dt = time.time() - self.lastTime
    if dt > 10:
      self.lastTime = time.time()
      if self.fileCounter > 0 and self.bytesDownloaded > 0:
        speed = self.bytesDownloadedTemp / dt
        self.bytesDownloadedTemp = 0
        timePassedSeconds = time.time() - self.startTime
        etaSeconds = self.bytesLeft / (self.bytesDownloaded / timePassedSeconds)
        percDone = min(100, self.fileCounter / self.filecount * 100)
        etaStr = 'unknown'
        if etaSeconds < 99999999:
          etaStr = self._formatSeconds(etaSeconds)
        extra = {
          'type': 'task_progress',
          'svn_state': 'checkout_running',
          'filesDone': self.fileCounter,
          'filesTotal': self.filecount,
          'bytesDownloaded': self.bytesDownloaded,
          'bytesTotal': self.bytesTotal,
          'percentDone': percDone,
          'dlSpeedPerSec': speed,
          'etaSeconds': etaSeconds,
        }
        if hasattr(self, 'shellTask'):
          self.shellTask._fillLoggerTaskData(extra)
        logger.info('{percentDone:6.2f}% | {filesDone: >6} / {filesTotal:} files | {bytesDownloaded: >9} / {bytesTotal:} | {dlSpeed: >9}/s | ETA: {eta:}'.format(
          filesDone = self.fileCounter,
          filesTotal = self.filecount,
          bytesDownloaded = human_readable_size(self.bytesDownloaded),
          bytesTotal = human_readable_size(self.bytesTotal),
          percentDone = percDone,
          dlSpeed = human_readable_size(speed),
          eta = etaStr
        ), extra = extra)

class _SVNUpdateOutputProcessor:
  """helper class for svn update"""
  def __init__(self):
    self.fileCounter = 0
    self.stats = {}
    self.lastTime = time.time()

  def report(self):
    if self.fileCounter > 0:
      fileStats = []
      if 'A' in self.stats:
        fileStats.append('{: >6} Added'.format(self.stats['A']))
      if 'D' in self.stats:
        fileStats.append('{: >6} Deleted'.format(self.stats['D']))
      if 'U' in self.stats:
        fileStats.append('{: >6} Updated'.format(self.stats['U']))
      if 'C' in self.stats:
        fileStats.append('{: >6} Conflicted'.format(self.stats['C']))
      if 'M' in self.stats:
        fileStats.append('{: >6} Merged'.format(self.stats['M']))
      if 'B' in self.stats:
        fileStats.append('{: >6} Broken'.format(self.stats['B']))
      if len(fileStats) > 0:
        #c = proc.io_counters()
        filesStr = 'svn update file progress: ' + ', '.join(fileStats)
        extra = {
          'type': 'task_progress',
          'svn_state': 'updating',
          'stats': self.stats,
        }
        if hasattr(self, 'shellTask'):
          self.shellTask._fillLoggerTaskData(extra)
        logger.info(filesStr, extra = extra)

  def finalReport(self):
    self.report()

  def progress(self, line):
    line = line.strip()
    self.fileCounter += 1
    res = svn_update_re.findall(line)
    if res:
      res = res[0]
      mode = res[0]
      if mode == 'Updating':
        return
      if not mode in self.stats:
        self.stats[mode] = 0
      self.stats[mode] += 1
    else:
      extra = {
        'type': 'task_progress',
        'svn_state': 'updating',
      }
      if hasattr(self, 'shellTask'):
        self.shellTask._fillLoggerTaskData(extra)
      logger.info(line, extra = extra)

    dt = time.time() - self.lastTime
    if dt > 10:
      self.lastTime = time.time()
      self.report()

def svnCheckout(**execCtx):
  # look how much stuff is out there
  pr = _SVNListOutputProcessor()
  shellTask = zoe_ci.tasks.ShellTask('svn list -v -R {vcs.url:} --non-interactive --username "{vcs.username:}" --password "{vcs.password:}"', callbackClass=pr, **execCtx)
  ret, _ = shellTask.run()
  svn_files, total_bytes = pr.getResults()
  if ret == 0:
    extra = {
      'svn_state': 'about_to_checkout',
      'fileCount': len(svn_files),
      'fileSize': total_bytes,
    }
    shellTask._fillLoggerTaskData(extra)
    logger.info('About to download {fileCount:} files / {fileSize:} ...'.format(
      fileCount = len(svn_files),
      fileSize = human_readable_size(total_bytes)
    ), extra = extra)

  reporter = _SVNCheckoutOutputProcessor(svn_files, total_bytes, **execCtx)
  ret, _ = exec('svn checkout {vcs.url:} . --config-option config:miscellany:use-commit-times=yes --non-interactive --username "{vcs.username:}" --password "{vcs.password:}" -r {vcs.targetRevision:}''', callbackClass=reporter, **execCtx)
  return ret == 0

def svnCleanup(**execCtx):
  logger.info("Cleaning up svn ...", extra = {'svn_state': 'cleanup'})
  retA, _ = exec('svn cleanup . --non-interactive', callbackClass=_ProgressReporterSimple(), optional=True, **execCtx)
  retB, _ = exec('svn cleanup . --remove-unversioned --remove-ignored --vacuum-pristines --include-externals --non-interactive', callbackClass=_ProgressReporterSimple(), optional=True, **execCtx)
  return retA == 0 and retB == 0

def svnResetPath(**execCtx):
  if os.name == 'nt':
    ret = exec('rmdir /S /Q "{WORKSPACE:}\\{vcs.outPath:}"', title='recursive delete', **execCtx)
    if ret == 0:
      return True
    else:
      logger.error("Unable to reset svn path {} - files still in use?".format(execCtx['vcs'].outPath))
      return False
  recursive_delete(vcs.outPath)
  return True

def _parseSVNInfo(lines):
  res = {}
  for i in range(0, len(lines)):
    args = lines[i].strip().split(': ')
    if(len(args) == 2):
      res[args[0]] = args[1]
  if 'Revision' in res:
    res['Revision'] = int(res['Revision'])
  else:
    res['Revision'] = 0
  return res

def _getSVNInfoLocal(**execCtx):
  ret, lines = exec('svn info . --non-interactive', optional=True, **execCtx)
  if ret == 0:
    return _parseSVNInfo(lines), False
  elif ret == 1:
    # E155007: '<>' is not a working copy
    if len(lines) > 0 and lines[0].find('E155007'):
      return None, True
  return None, False

def _getSVNInfoRemote(**execCtx):
  ret, lines = exec('svn info --non-interactive --username "{vcs.username:}" --password "{vcs.password:}" {vcs.url:}', optional=True, **execCtx)
  if ret == 0:
    return _parseSVNInfo(lines)
  return None

def svnUpdate(**execCtx):
  with GenericTask("svn update") as t:
    # ok, look at the local directory first
    svnInfo_local, notAnSVNRepo = _getSVNInfoLocal(**execCtx)
    if svnInfo_local:
      svnInfo_remote = _getSVNInfoRemote(**execCtx)
      if svnInfo_remote:
        if svnInfo_local['Revision'] == svnInfo_remote['Revision']:
          logger.info("Updating to revision {} ...".format(
            svnInfo_remote['Revision']
          ), extra = {
            'svn_state': 'updating_to_resume',
            'svn_revision_to': svnInfo_remote['Revision']
          })
        else:
          logger.info("Updating {} revisions from {} to {} ...".format(
            svnInfo_remote['Revision'] - svnInfo_local['Revision'],
            svnInfo_local['Revision'], svnInfo_remote['Revision']
          ), extra = {
            'svn_state': 'updating_to',
            'svn_revision_from': svnInfo_local['Revision'],
            'svn_revision_to': svnInfo_remote['Revision']
          })

      pr = _SVNUpdateOutputProcessor()
      ret, lines = exec('svn update . --force --accept tf --config-option config:miscellany:use-commit-times=yes --non-interactive --username "{vcs.username:}" --password "{vcs.password:}" -r {vcs.targetRevision:}', callbackClass=pr, optional=True, **execCtx)
      if ret == 0:
        logger.info("Updating done.", extra = {'svn_state': 'update_done'})
        return True
      elif ret == 1:
        #svn: E155037: Previous operation has not finished; run 'cleanup' if it was interrupted
        if len(lines) > 0 and lines[0].find('E155037'):
          if svnCleanup(**execCtx):
            return False
          else:
            logger.warn('Unable to clean up. Resetting ...', extra = {'svn_state': 'cleanup'})
            if not svnResetPath(**execCtx):
              logger.fatal('Unable to reset path')
              return False
            return False

      return False
    if notAnSVNRepo:
      logger.warn('Working checkout is completely corrupted: {WORKSPACE:}\\{vcs.outPath:} - Resetting...'.format(WORKSPACE= os.environ['WORKSPACE'], **execCtx), extra = {'svn_state': 'corrupted'})
      if not svnResetPath(**execCtx):
        logger.fatal('Unable to reset path')
        return False
      return False
    return False

def logSVNVersion():
  """For debugging purposes, logs the svn version"""
  try:
    svn_version = exec('svn --version --quiet', optional=True)[1][0]
    logger.debug('Found svn version {svn_version:}'.format(svn_version = svn_version), extra = {'svn_version': svn_version})
  except:
    logger.warn('Unable to get svn version')

def svnSync(vcs: VCS):
  with GenericTask("svn sync") as t:
    execCtx = {'vcs': vcs, 'parentTask': t, 'workingDirectory': vcs.outPath}
    res = False

    if not exec_available('svn'):
      raise Exception('svn executable not usable')

    logSVNVersion()

    os.chdir(os.environ['WORKSPACE'])

    if os.path.exists(vcs.outPath):
      for i in range(1, 5):
        if svnUpdate(**execCtx):
          res = True
          break
    else:
      res = svnCheckout(**execCtx)
    return res