@echo off
:: Change working directory to this script's path
cd /D "%~dp0"

echo Setting up python environment ...
python -m venv .venv
call .venv\\Scripts\\activate.bat
pip --disable-pip-version-check -q install -r requirements.txt

echo Running ...
python -m uvicorn ZoeServer.main:app --reload
