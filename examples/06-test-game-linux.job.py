import zoe_ci.work
import zoe_ci.tasks

class Example_06_SimpleScriptJob(zoe_ci.work.Job):
  def run(self, *args):

    with zoe_ci.tasks.GenericTask():
      # running in linux
      command_to_run = "cd " + " && " + "~/trunk/BinLinux/BeamNG.drive.x64 " + ' -lua extensions.load test/singleLevel -testlevel west_coast_usa -nocrashreport -noColorStdOutLog -quitonfatalerror -noninteractive -batch -nosteam'

      beamng = zoe_ci.tasks.ShellTask(command_to_run, throw=False, timeout=5)
      with beamng as process:
        while process.readable():
          line = process.readline()
          if not line:
            break
          print(">>> LINE: " + str(line.rstrip()))
          if line.find('*** Loaded everything in') != -1:
            process.write('shutdown(0)')
