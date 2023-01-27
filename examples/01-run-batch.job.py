import zoe_ci
import zoe_ci.work
import zoe_ci.utils

from zoe_ci.tasks import ShellTask

class Example_01_SimpleBatch(zoe_ci.work.Job):
  def run(self, *args):
    print(' * zoe_ci Machine UUID: {}'.format(self.env['machine_uuid']))

    print(' * Windows version:', zoe_ci.utils.runCommandSimple('ver'))

    exitCode, output = ShellTask('echo %APPDATA%', shell=True).run()
    print(' * Appdata folder:', ''.join(output))

    for v in ['COMPUTERNAME', 'TIME', 'DATE', 'USERNAME', 'NUMBER_OF_PROCESSORS', 'APPDATA']:
      print(' * ', v, '=', zoe_ci.utils.getWindowsShellVariable(v))

    exitCode, output = ShellTask('echo Hello world from the windows shell', title='Hello world', shell=True).run()
    print(" * Hello world finished. Return code = ", exitCode, '/ Output = ', output)
