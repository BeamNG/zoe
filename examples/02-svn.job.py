import Zoe.work
import Zoe.utils

class Example_02_SVN(Zoe.work.Job):
  def run(self, *args):
    Zoe.utils.VCS(type='svn', outPath='trunk', url='http://your/svn/URL/').sync()
