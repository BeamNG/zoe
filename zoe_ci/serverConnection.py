import websocket
import threading
import time
import queue
import json
import random
import os
import logging
from datetime import datetime
from typing import Union

import zoe_ci.utils
import zoe_ci.tasks
import zoe_ci.work

MAX_RECONNECT_TIME_SEC = 300
MIN_RECONNECT_TIME_SEC = 3

logger = logging.getLogger('Websocket')

class CommThread(threading.Thread):
  def __init__(self, eventHandler, env, executorInfo):
    threading.Thread.__init__(self)
    self.env = env
    self.executorInfo = executorInfo
    self.fullyConnected = False
    self.shutdown = False
    self.disconnectionDatetime = None
    self.ws = None
    self.eventHandler = eventHandler
    self.sendQueue = queue.Queue()
    self.recvQueue = queue.Queue()
    self.sleepCooldown = MIN_RECONNECT_TIME_SEC

  def on_error(self, wsapp, ex):
    self.fullyConnected = False
    logger.error("error: " + str(ex))

  def on_close(self, wsapp, close_status_code, close_msg):
    self.fullyConnected = False
    self.disconnectionDatetime = datetime.now()
    if close_status_code or close_msg:
      logger.warning("closed: " + str(close_status_code) + " - " + str(close_msg))

  def on_data(self, wsapp, msgRaw, dataType, continueData):
    #logger.info("on_message: " + str(msgRaw))
    self.recvQueue.put([msgRaw, dataType])
    self.eventHandler.dataReady.acquire()
    self.eventHandler.dataReady.notify_all()
    self.eventHandler.dataReady.release()

  def on_open(self, wsapp):
    self.fullyConnected = True
    self.sleepCooldown = MIN_RECONNECT_TIME_SEC # reset the disconnection cooldowns
    #logger.debug("connected")
    if self.disconnectionDatetime and not self.shutdown:
      logger.info("reconnected after {:.2f} seconds".format((datetime.now() - self.disconnectionDatetime).total_seconds()))
      self.disconnectionDatetime = None
    while self.ws and not self.sendQueue.empty():
      self._send(self.sendQueue.get())

    self._send({'type': 'register', 'data': self.executorInfo})

  def _threadEntry(self):
    #logger.info("thread {} started".format(threading.current_thread().name))

    while True:
      serverURL = os.environ.get('WS_SERVER')
      if not self.shutdown:
        logger.debug("connecting to server {}".format(serverURL))
      self.ws = websocket.WebSocketApp(serverURL, on_error = self.on_error, on_close = self.on_close, on_data = self.on_data, on_open = self.on_open)
      #websocket.enableTrace(True)
      self.ws.run_forever()
      # reconnect cooldowns: double every time we disconnect
      sleepTime = random.randint(self.sleepCooldown, self.sleepCooldown * 2) # use random so all clients wont hammer the server at the same time
      self.sleepCooldown = min(MAX_RECONNECT_TIME_SEC, self.sleepCooldown * 2)
      if self.ws and not self.shutdown:
        logger.info("reconnecting in {} seconds".format(sleepTime))
        time.sleep(sleepTime)
      logger.info("thread {} DONE".format(threading.current_thread().name))

  def _encodeMessage(self, msg: Union[int, str, dict]):
    if type(msg) is str:
      return msg
    elif type(msg) is dict:
      msg = json.dumps(msg, default=lambda o: '<not serializable>')
    else:
      msg = str(msg)
    return msg

  def _send(self, msgRaw):
    msg = self._encodeMessage(msgRaw)
    if not self.ws or not self.ws.sock:
      logger.error('error: socket gone')
      return
    try:
      self.ws.send(msg)
    except websocket.WebSocketConnectionClosedException as ex:
      logger.error('disconnected')
      self.ws = None
    except Exception as ex:
      logger.exception('exception: ' + str(ex))
      self.ws = None


  def send(self, msgRaw):
    #logger.info(">> " + str(msgRaw))
    if not self.fullyConnected:
      self.sendQueue.put(msgRaw)
      return
    self._send(msgRaw)

  def stopThread(self):
    if self.ws:
      self.ws.keep_running = False
    self.shutdown = True

class CommsLogHandler(logging.StreamHandler):
  def __init__(self, comm, name, *args, **kwargs):
    logging.StreamHandler.__init__(self, name, *args, **kwargs)
    self.comm = comm
    self.dummyLog = logging.LogRecord(None,None,None,None,None,None,None)
    self._logRunning = False

  def emit(self, record):
    if self._logRunning:
      # prevent recursive calling due to logging system
      return
    self._logRunning = True

    data = {
      'type': 'log', # can be overwritten with extra
      #'t': record.relativeCreated, # this is not really usable
      't': datetime.now().isoformat(),
      'l': record.levelname,
      'm': record.msg,
    }

    if zoe_ci.tasks.GenericTask.lastTask:
      data['task_id'] = zoe_ci.tasks.GenericTask.lastTask.taskid
      data['build_id'] = zoe_ci.work.Runtime.buildId

    for k, v in record.__dict__.items():
      if k not in self.dummyLog.__dict__:
        if type(v) == tuple:
          pass
          #data[k] = dict(v) # preserve keys correctly ...
        else:
          if k == 'message' and v == record.msg or k == 'asctime':
            continue
          data[k] = v
    self.comm.send(data)
    self._logRunning = False

def createComms(cb, env, executorInfo):
  comm = CommThread(cb, env, executorInfo)
  thread = threading.Thread(target = comm._threadEntry)
  thread.daemon = True
  thread.start()
  # install the log listener on the root logger to catch all logs
  commsHandler = CommsLogHandler(comm, 'CommsLogHandler')
  logging.getLogger().addHandler(commsHandler)
  return comm
