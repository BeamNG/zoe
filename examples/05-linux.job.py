import zoe_ci
import zoe_ci.work
import zoe_ci.utils

class Example_05_SimpleBatch(zoe_ci.work.Job):
  def run(self, *args): 

    with zoe_ci.tasks.GenericTask():
      self.logger.info('Hello world 1')
      print(' * zoe_ci Machine UUID: {}'.format(self.env['machine_uuid']))

    print(' * Linux Kernel Version:', zoe_ci.utils.runCommandSimple('uname -r'))

    exitCode, output = zoe_ci.tasks.ShellTask('echo "hello"', shell=True).run()
    print(' * Echo', ''.join(output))

    for v in ['HOSTNAME', 'HOSTTYPE', 'HOME', 'LOGNAME', "SHELL"]:
      print(' * ', v, '=', zoe_ci.utils.getUnixShellVariable(v))

    exitCode, output = zoe_ci.tasks.ShellTask('echo Hello world from the Linux shell', title='Hello world', shell=True).run()
    print(" * Hello world finished. Return code = ", exitCode, '/ Output = ', output)
