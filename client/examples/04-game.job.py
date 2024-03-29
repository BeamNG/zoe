import Zoe
import Zoe.work
import Zoe.utils

class Example_04_run_game(Zoe.work.Job):
  def run(self, *args):
    Zoe.utils.VCS(type='svn', outPath='game_trunk', url='http://svn.intranet.beamng.com/game/trunk').sync()
    self.logger.info('svn all good :)')
    common_game_cmd = 'game_trunk/Bin64/BeamNG.drive.x64.exe -console -lua extensions.load("test/singleLevel") -testlevel west_coast_usa -nocrashreport -noColorStdOutLog '

    # there are several ways to run the game :)

    # 0) very simply execute it:
    Zoe.tasks.ShellTask(common_game_cmd + ' -lua shutdown(0)').run()

    # 1) simply executing it:
    retCode, linesOut = Zoe.tasks.ShellTask(common_game_cmd + ' -lua shutdown(0)', throw=False).run()

    # 2) run with some timeout:
    retCode, linesOut = Zoe.tasks.ShellTask(common_game_cmd, throw=False, timeout=3).run()

    # 3) interactively - read stdout/err and write to stdin:
    with Zoe.tasks.GenericTask('launchGameInteractive'):
      beamng = Zoe.tasks.ShellTask(common_game_cmd + '-luastdin', throw=False, timeout=30)
      with beamng as process:
        while process.readable():
          line = process.readline()
          if not line:
            break
          print(">>> LINE: " + str(line.rstrip()))
          if line.find('*** Loaded everything in') != -1:
            process.write('shutdown(0)')
            #process.kill()
      print('retCode = ' + str(beamng.retCode))
      print('linesOut = ' + str(beamng.linesOut))


