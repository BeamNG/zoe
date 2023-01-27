import os
import subprocess
import time
import hashlib
import datetime
import logging

import zoe_ci.utils

class GenericTask:
  """A simple placeholder that describes something happening in a given timeframe between __enter__ and __exit__ (use with 'with')"""
  globalTaskStack = []
  lastTask = None

  def __init__(self, *args: list, **kwargs: dict) -> None:
    self.logger = logging.getLogger(self.__class__.__name__)
    self.taskName = kwargs.get('title', self.__class__.__name__)
    if type(self) == GenericTask and len(args) > 0:
      self.taskName = args[0]
    self.siblings = {}
    self.taskid = f"/{self.taskName}/"
    self.result = True


    if GenericTask.globalTaskStack: # empty lists eval to False
      parentTask = GenericTask.globalTaskStack[-1]
      if not self.taskName in parentTask.siblings:
        parentTask.siblings[self.taskName] = 0
      parentTask.siblings[self.taskName] += 1

      self.taskid = parentTask.__dict__.get('taskid', '/') + '{}#{}/'.format(self.taskName, parentTask.siblings[self.taskName])

  def __enter__(self, *args, **kwargs):
    self.startTime = datetime.datetime.now().isoformat()
    extra = kwargs.get('extra', {})
    extra.update({
      'type': 'task_begin',
      'task_id': self.taskid,
    })
    self.logger.debug(self.taskName, extra = extra)
    GenericTask.globalTaskStack.append(self)
    GenericTask.lastTask = self
    return self

  def __exit__(self, *args, **kwargs):
    self.endTime = datetime.datetime.now().isoformat()
    GenericTask.lastTask = GenericTask.globalTaskStack.pop()
    extra = kwargs.get('extra', {})
    extra.update({
      'type': 'task_end',
      'task_id': self.taskid,
      'result': self.result,
    })
    self.logger.debug(self.taskName, extra = extra)

  def _fillLoggerTaskData(self, d):
    """for the UI, etc"""
    d['task_id'] = self.taskid

class ShellTask(GenericTask):
  def __init__(self, *args, **kwargs):
    super(ShellTask, self).__init__(*args, **kwargs)

    self.vcs = kwargs.get('vcs', zoe_ci.utils.VCS())
    self.useShell = kwargs.get('shell', None)
    self.cmdEnv = {'vcs': self.vcs}
    self.cmdEnv.update(os.environ)
    if len(args) != 1:
      raise Exception('Only one positional argument allowed: the command itself')

    _cmd = args[0].format(**self.cmdEnv) + ' ' + kwargs.get('cmdPostfix', '')

    # convert / to \\ on windows for the executable
    cmdArgs = _cmd.split(' ', maxsplit=1) + [''] # [''] is the default fallback for no arguments below
    try:
      # if os.name == 'nt':
      executablePath = cmdArgs[0].replace('/', '\\')
      if executablePath.lower().find('.exe') != -1: # if cmd contains .exe, do not use the shell by default
        self.useShell = False
        self.cmd = executablePath + ' ' + cmdArgs[1]
      self.cmd = self.cmd.rstrip()
      #print(">>> ", self.cmd)
    except:
      self.cmd = _cmd

    if self.useShell is None:
      self.useShell = True

    self.cmd_log = self.cmd
    if self.vcs and self.vcs.password:
      self.cmd_log = self.cmd.replace(self.vcs.password, '<PASSWORD>') # to not leak the password into log files
    self.title = kwargs.get('title', None)
    if not self.title:
      self.title = ' '.join(self.cmd_log.split(' ')[0:3])[0:20]
    self.cmdHash = hashlib.sha256(self.cmd.encode()).hexdigest()
    self.optional = kwargs.get('optional', False)
    self.callbackClass = kwargs.get('callbackClass', None)
    if self.callbackClass:
      self.callbackClass.shellTask = self # tell the progress reporting class about the execution context
    self.procState = 'idle'
    self.retCode = None
    self.throw = kwargs.get('throw', True)
    self.timeout = kwargs.get('timeout', None)
    self.exitTimeout = kwargs.get('exitTimeout', 10) # wait 10 seconds between the pipes closing and killing the process
    self.parentTask = kwargs.get('parentTask', None)
    self.workingDirectory = os.path.join(os.environ.get('WORKSPACE', ''), kwargs.get('workingDirectory', ''))

  def __enter__(self):
    self.procState = 'starting'
    extra = {
      'type': 'task_begin',
      'task_id': self.taskid,
      'cmd_log': self.cmd_log,
      'cmdHash': self.cmdHash,
      'optional': self.optional,
      'procState': self.procState,
    }

    super(ShellTask, self).__enter__(title=self.title, extra=extra) # will fire task_begin

    if self.workingDirectory:
      os.makedirs(self.workingDirectory, exist_ok = True)

    processEnv = dict(filter(lambda elem: type(elem[0]) == str and type(elem[1]) == str, self.cmdEnv.items()))

    del processEnv['SVN_USER']
    del processEnv['SVN_PASS']

    #print("CMD: ", self.cmd)

    pr = subprocess.Popen(self.cmd,
      cwd=self.workingDirectory,
      stdin=subprocess.PIPE,
      stdout=subprocess.PIPE,
      stderr=subprocess.STDOUT,
      shell=self.useShell,
      universal_newlines=True,
      bufsize=32000,  # 0=unbuffered, 1=line-buffered, else buffer-size
      #close_fds=True,
      #env=processEnv,
    )
    self.procState = 'running'
    self.linesOut = []
    # little shortcut to make the usage easier
    pr.readable = self.readable
    pr.writable = self.writable
    pr.readline = self.readline
    pr.write = self.write
    pr.kill = self.__killProcess
    self.process = pr
    self.startTime = time.time()
    return self.process

  def _checkProcessTimeout(self):
    timeRunning = time.time() - self.startTime
    if self.timeout and timeRunning > self.timeout:
      self.logger.warn('command timed out and killed after {} seconds'.format(timeRunning))
      self.__killProcess()
      if self.throw:
        raise Exception('command timeout')
      return True
    return False


  def run(self):
    with self as process:
      while process.readable():
        if not process.readline():
          break
    return self.retCode, self.linesOut

  def readable(self):
    if self._checkProcessTimeout():
      self.result = False
      return None
    return self.process.stdout.readable()

  def readline(self, bufferLines = True):
    line = self.process.stdout.readline()
    if line is None:
      return None
    line = line.rstrip()
    #print(line.strip())
    if len(line) == 0:
      return line
    self.logger.debug(line, extra = {'type': 'task_log', 'task_id': self.taskid})
    if bufferLines:
      self.linesOut.append(line)
    if self.callbackClass:
      self.callbackClass.progress(line)
    return line

  def writable(self):
    return self.process.stdin.writable()

  def write(self, data):
    if not self.process.stdin.writable():
      print("Error: stdin not write-able")
      return
    self.process.stdin.write(data)
    self.process.stdin.flush()

  def __killProcess(self):
    if os.name == 'nt':
      subprocess.call(['taskkill', '/F', '/T', '/PID', str(self.process.pid)])
    else:
      try:
        os.kill(pid, signal.SIGTERM)
      except:
        return


  def __exit__(self, type, value, traceback):
    if not type is None:
      # we got an exception, re-raise exception by returning false
      return False

    # pipes are closed already, wait for the process to quit properly
    lastTime = time.time()
    exitTime = time.time()
    while self.process.poll() is None:
      # wait until process exits
      time.sleep(0.01)
      if time.time() - lastTime > 3:
        self.logger.warning("waiting since {:0.0f} seconds for process to exit...".format(time.time() - exitTime))
        lastTime = time.time()
      if time.time() - exitTime > self.exitTimeout:
        self.logger.error("Killing process after waited {:0.0f} seconds for process to exit...".format(time.time() - exitTime))
        self.__killProcess()
        self.result = False

    self.procState = 'done'
    self.retCode = self.process.poll()
    extra = {
      'type': 'task_end',
      'task_id': self.taskid,
    }
    if self.retCode != 0 and not self.optional:
      extra['type'] = 'task_error'

      error_msg = '*** cmd failure ***\n{}\n failed with return code {} (0x{:02X}) - {}'.format(self.cmd_log, self.retCode, self.retCode, '\n'.join(self.linesOut[:3]))
      self.logger.error(error_msg, extra = extra)
      self.result = False
      try:
        if self.throw:
          raise zoe_ci.utils.ZoeException(error_msg)
      except zoe_ci.utils.ZoeException as e:
        self.logger.error(f"Exception: {e}")
        pass

    if self.callbackClass and hasattr(self.callbackClass, 'finalReport'):
      self.callbackClass.finalReport()

    extra['lines'] = self.linesOut

    # should be all closed now, stop the parent class
    super(ShellTask, self).__exit__(extra) # will fire task_end
