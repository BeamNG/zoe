# Zoe Server

This is the Restful API backend implemented in [FastAPI](https://fastapi.tiangolo.com) for the Zoe architecture.
It provides the communication endpoints for the clients, executors and the UI.

# Installation

We are using [python virtual environments](https://docs.python.org/3/tutorial/venv.html) in this project to not clutter and conflict with the system python installation.

## Windows - VScode development environment
```batch
git clone http://gitlab/beamng/zoe.git
cd zoe\server\api-backend
python -m venv .venv
call .venv\\Scripts\\activate.bat
pip install -r requirements.txt
```

You should be able to press F5 in VScode to start.
Otherwise you can also start manually:
```batch
uvicorn ZoeServer.main:app --reload
```

## Linux - Production environment
```bash
# for the tools
apt install subversion git sqlite3

# the main program:
git clone http://gitlab/beamng/zoe.git
cd zoe/server/api-backend
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt

# install nginx site
cp misc/ZoeServer-nginx /etc/nginx/sites-available/ZoeServer
ln -s /etc/nginx/sites-available/ZoeServer /etc/nginx/sites-enabled/
systemctl restart nginx.service

# install service
cp misc/ZoeServer.service /etc/systemd/system/ZoeServer.service
# !!!
# Now fix your installation path in /etc/systemd/system/ZoeServer.service (/home/testrunner)
# !!!
systemctl start ZoeServer.service
```

You can look at  the logs like this:
```bash
journalctl -u ZoeServer
```

Or run the server manually:

```bash
uvicorn ZoeServer.main:app --reload
```
