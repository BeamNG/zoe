import zoe_ci.work
import zoe_ci.tasks

class Example_00_minimal(zoe_ci.work.Job):
  def run(self, *args):

    with zoe_ci.tasks.GenericTask():
      self.logger.info('Hello world 1')
    with zoe_ci.tasks.GenericTask():
      self.logger.info('Hello world 2')

    zoe_ci.tasks.ShellTask('echo 123').run()

    with zoe_ci.tasks.GenericTask():
      self.logger.info('Hello world 3')
      print(zoe_ci.tasks.ShellTask('echo Hello').run())
