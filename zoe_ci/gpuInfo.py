import os
import logging

logger = logging.getLogger('GPU')

if os.name == 'nt':
  try:
    import wmi
  except Exception:
    wmi = None
    logger.exception("wmi module not found")

try:
  import GPUtil
except Exception:
  GPUtil = None
  logger.exception("GPUtil not installed, Nvidia GPU info not available")

try:
  from pyadl import *
except Exception:
  pyadl = None
  logger.exception("pyadl import error, AMD GPU info not available")

class NvidiaGpuInfo:
    """
    Nvidia Class for getting GPU information
    """
    def __init__(self) -> None:
      self.list_gpus = []
      try:
        self.gpus = GPUtil.getGPUs()
        self.gpuCount = len(self.gpus)
      except Exception:
        self.gpuCount = 0
        logger.exception("An error occurred while getting Nvidia GPU info")

    def getGpuInfo(self) -> list:
      if self.gpuCount > 0:
        for gpu in self.gpus:
            gpu_name = gpu.name
            gpu_load = f"{gpu.load*100}%"
            gpu_free_memory = round(gpu.memoryFree)
            self.list_gpus.append(
                (
                  gpu_name,
                  gpu_free_memory,
                  gpu_load,
                )
            )
        return self.list_gpus
      else:
        return []


class AMDGpuInfo:
    """
    AMD Class for getting GPU information
    """
    def __init__(self) -> None:
      self.gpus_info = []
      self.gpuCount = 0
      if pyadl is not None:
        
        try:
          self.gpus = ADLManager.getInstance().getDevices()
          self.gpuCount = len(self.gpus)
        except Exception:
          logger.exception("An error occurred while getting AMD GPU info")

    def getGpuInfo(self) -> list:
      """
      build gpu info list for AMD
      """
      try:
        for gpu in self.gpuCount:
            self.gpu = pyamdgpuinfo.get_gpu(gpu)
            gpu_name = self.gpu.name
            gpu_vram = self.gpu.query_vram_usage()
            gpu_load = self.gpu.query_load()
            self.gpus_info.append(
                (
                  gpu_name,
                  f"{round(gpu_vram / (1024 * 1024))} MB",
                  f"{gpu_load*100}%",
                )
            )
      except Exception:
          logger.exception("An error occurred while getting AMD GPU info")
          return []
      return self.gpus_info

class WindowsGpuInfo:
  """
  class windowsGpuInfo get gpu info for windows
  """
  def __init__(self) -> None:
    self.list_gpus = []
    self.gpuCount = 0
    if os.name == 'nt':
      self.c = wmi.WMI()
      if self.c.Win32_VideoController():
        self.gpuCount = len(self.c.Win32_VideoController())
    else:
      self.c = None

  def getGpuInfo(self) -> list:
    if os.name == 'nt' and self.c:
      name = self.c.Win32_VideoController()[0].Name
      ram = self.c.Win32_VideoController()[0].AdapterRAM
      ram = f"{round(ram / (1024 * 1024))} MB"
      self.list_gpus.append(name)
      self.list_gpus.append(ram)
      return self.list_gpus

class GpuInfo:
  """
  class GpuInfo get gpu info for windows, linux and mac
  """
  def __init__(self) -> None:
    self.gpus = []
    self.nvidia_client = NvidiaGpuInfo()
    self.amd_client = AMDGpuInfo()
    self.windows_client = WindowsGpuInfo()

  def _build_gpu_list(self) -> list:
    if self.nvidia_client.gpuCount > 0:
      self.gpus.extend(self.nvidia_client.getGpuInfo())

    elif self.amd_client.gpuCount > 0:
      self.gpus.extend(self.amd_client.getGpuInfo())

    elif self.windows_client.gpuCount > 0:
      self.gpus.extend(self.windows_client.getGpuInfo())
      
    return self.gpus
  
  def getGpuInfo(self) -> list:
    return self._build_gpu_list()
  
  def getGpuCount(self) -> int:
    return len(self.gpus)
