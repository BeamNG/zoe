import sys, os
import logging
from dotenv import load_dotenv, find_dotenv

from fastapi import FastAPI, Request
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from fastapi.middleware.cors import CORSMiddleware

import ZoeServer.config, ZoeServer.auth, ZoeServer.models, ZoeServer.database
import ZoeServer.test_platform

logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

# add the Zoe client to the path
depsPath = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'client'))
sys.path.insert(0, depsPath)
# and the server deps
depsPath = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'dependencies'))
sys.path.insert(0, depsPath)


load_dotenv(find_dotenv(filename=".env.default"))
load_dotenv(find_dotenv(filename=".env"))
#print('Config: ' + str(dotenv_values(".env"))) 
#print('OS2: ' + os.environ.get('SERVER_DATA_PATH', None)) # Example to get config

app = FastAPI(
  title='Zoe API Server',
  description='Zoe Websocket Server',
  version='0.1.0',
  contact={
    "name": "BeamNG GmbH",
    "url": "http://gitlab/beamng/zoe",
    "email": ""
    },
  )

origins = [
  "http://127.0.0.1",
  "http://127.0.0.1:8000",
  "http://zoe.intranet.beamng.com",
]

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

# redirect / to /docs
@app.get("/", include_in_schema=False)
async def docs_redirect():
  return RedirectResponse(url='/admin-ui/app/dashboard/executors')


templatesPath = os.path.normpath(os.path.join(os.path.dirname(__file__), 'templates'))
templates = Jinja2Templates(directory=templatesPath)

# hacky example
@app.get("/chat/")
async def get(request: Request):
  return templates.TemplateResponse("chatExample.html", {"request":request})

## modules below ...

import ZoeServer.ldap
if ZoeServer.ldap.available():
  app.include_router(ZoeServer.ldap.router)
#else:
#  logger.warning("LDAP module disabled. Required packages or config missing.")

import ZoeServer.vcs.svn.api as svn_api
if svn_api.available():
  app.include_router(svn_api.router)
else:
  logger.warning("Subversion module disabled. Required packages or config missing.")

import ZoeServer.vcs.git.api as git_api
if git_api.available():
  app.include_router(git_api.router)
else:
  logger.warning("GIT module disabled. Required packages or config missing.")

import ZoeServer.jobUtils as jobUtils
if not jobUtils.available():
  logger.error("Job module is required to work")
  #sys.exit(1)

app.include_router(ZoeServer.auth.router)
#app.include_router(ZoeServer.test_platform.router)


ZoeServer.database.setupDB()


import ZoeServer.ws.main
if ZoeServer.ws.main.available():
  app.include_router(ZoeServer.ws.main.router)
else:
  logger.warning("WS module disabled. Required packages or config missing.")
