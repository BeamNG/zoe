import Zoe
import Zoe.work
import Zoe.utils

class Example_05_SimpleBatch(Zoe.work.Job):
  def run(self, *args): 

    with Zoe.tasks.GenericTask():
      self.logger.info('Hello world 1')
      print(' * Zoe Machine UUID: {}'.format(self.env['machine_uuid']))

    print(' * Linux Kernel Version:', Zoe.utils.runCommandSimple('uname -r'))

    exitCode, output = Zoe.tasks.ShellTask('echo "hello"', shell=True).run()
    print(' * Echo', ''.join(output))

    for v in ['HOSTNAME', 'HOSTTYPE', 'HOME', 'LOGNAME', "SHELL"]:
      print(' * ', v, '=', Zoe.utils.getUnixShellVariable(v))

    exitCode, output = Zoe.tasks.ShellTask('echo Hello world from the Linux shell', title='Hello world', shell=True).run()
    print(" * Hello world finished. Return code = ", exitCode, '/ Output = ', output)
