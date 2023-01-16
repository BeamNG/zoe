import Zoe.work
import Zoe.tasks

class Example_00_minimal(Zoe.work.Job):
  def run(self, *args):

    with Zoe.tasks.GenericTask():
      self.logger.info('Hello world 1')
    with Zoe.tasks.GenericTask():
      self.logger.info('Hello world 2')

    Zoe.tasks.ShellTask('echo 123').run()

    with Zoe.tasks.GenericTask():
      self.logger.info('Hello world 3')
      print(Zoe.tasks.ShellTask('echo Hello').run())
