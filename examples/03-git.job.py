import zoe_ci.work
import zoe_ci.utils

class Example_03_GIT(zoe_ci.work.Job):
  def run(self, *args):
    zoe_ci.utils.VCS(type='git', outPath='zoe-main', url='http://your/git/url.git').sync()
