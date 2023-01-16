# Zoe Job framework

If you are new to Zoe, look at the architecture docs there: [misc/ZoeArch.md](misc/ZoeArch.md)

This repository is the client part of the Zoe architecture that executes work items on target machines.

It consists of:
* a python library that implements the base primitives: [Zoe](Zoe)
* and several [examples](examples)

## Conventions

* All jobs should be in files named `*.job.py`. This way the version control systems can trigger jobs correctly.
* Only one job per file
* Try to keep complexity down as much as possible, increasing maintainability of the overall system
* Try to write the code in a cross-platform matter if simple enough (linux/windows/console)


### Installation
```batch
pip install zoe
```

to run:
```batch
python -m Zoe
```
## Development: start / testing

Run the solution in vscode with F5, see `.vscode/launch.json`

## Manual testing

just execute any .job.py file in python:

```batch
examples\\01-simple-svn-checkout.job.py
```