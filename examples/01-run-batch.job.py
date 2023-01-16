import Zoe
import Zoe.work
import Zoe.utils

from Zoe.tasks import ShellTask

class Example_01_SimpleBatch(Zoe.work.Job):
  def run(self, *args):
    print(' * Zoe Machine UUID: {}'.format(self.env['machine_uuid']))

    print(' * Windows version:', Zoe.utils.runCommandSimple('ver'))

    exitCode, output = ShellTask('echo %APPDATA%', shell=True).run()
    print(' * Appdata folder:', ''.join(output))

    for v in ['COMPUTERNAME', 'TIME', 'DATE', 'USERNAME', 'NUMBER_OF_PROCESSORS', 'APPDATA']:
      print(' * ', v, '=', Zoe.utils.getWindowsShellVariable(v))

    exitCode, output = ShellTask('echo Hello world from the windows shell', title='Hello world', shell=True).run()
    print(" * Hello world finished. Return code = ", exitCode, '/ Output = ', output)
