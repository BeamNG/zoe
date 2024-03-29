import Zoe.work
import Zoe.utils

class Example_03_GIT(Zoe.work.Job):
  def run(self, *args):
    Zoe.utils.VCS(type='git', outPath='zoe-main', url='http://gitlab.intranet.beamng.com/beamng/zoe.git').sync()
