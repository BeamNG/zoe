import zoe_ci.work
import zoe_ci.utils

class Example_02_SVN(zoe_ci.work.Job):
  def run(self, *args):
    zoe_ci.utils.VCS(type='svn', outPath='trunk', url='http://your/svn/URL/').sync()
