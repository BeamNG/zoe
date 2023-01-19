# zoe_ci Job framework

If you are new to zoe_ci, look at the architecture docs there: [misc/ZoeArch.md](misc/ZoeArch.md)

This repository is the client part of the zoe_ci architecture that executes work items on target machines.

It consists of:
* a python library that implements the base primitives: [zoe_ci](zoe_ci)
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
python -m zoe_ci
```
## Development: start / testing

Run the solution in vscode with F5, see `.vscode/launch.json`

## Manual testing

just execute any .job.py file in python:

```batch
examples\\01-simple-svn-checkout.job.py
```