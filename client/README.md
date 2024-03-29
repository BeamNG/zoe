# Zoe Job framework

This is the client part of the Zoe architecture that executes work items on target machines.

It consists of:
* a python library that implements the base primitives: [Zoe](Zoe)
* and several [examples](examples)

## Conventions

* All jobs should be in files named `*.job.py`. This way the version control systems can trigger jobs correctly.
* Only one job per file
* Try to keep complexity down as much as possible, increasing maintainability of the overall system
* Try to write the code in a cross-platform matter if simple enough (linux/windows/console)

## Windows - VScode development environment

You can use the `run.bat` batch file which will do everything for you :)

### Manual installation
```batch
git clone http://gitlab/beamng/zoe.git
cd client
python -m venv .venv
call .venv\\Scripts\\activate.bat
pip install -r requirements.txt
```

to run:
```batch
python -m Zoe
```

### Installation as a service

Run `misc\windows-service\install_runas_admin.bat` with Administrator privileges.

## Linux

You can use the `run.sh` batch file which will do everything for you :)

### Manual installation
```bash
git clone http://gitlab/beamng/zoe.git
cd client
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

to run:
```bash
python3 -m Zoe
```

### Installation as a service
```bash
# install service (if you want)
cp misc/ZoeClient.service /etc/systemd/system/ZoeClient.service
# !!!
# Now fix your installation path in /etc/systemd/system/ZoeClient.service (/home/testrunner)
# !!!
systemctl start ZoeClient.service
```

## Development: start / testing

Run the solution in vscode with F5, see `.vscode/launch.json`

## Manual testing

just execute any .job.py file in python:

```batch
examples\\01-simple-svn-checkout.job.py
```