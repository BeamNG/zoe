import Zoe.work
import Zoe.utils

class Example_03_GIT(Zoe.work.Job):
  def run(self, *args):
    Zoe.utils.VCS(type='git', outPath='zoe-main', url='http://your/git/url.git').sync()
