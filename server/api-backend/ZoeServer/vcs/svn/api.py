from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
from .config import getSVNSettings
from .models import SVNRepo, SVNRepoCommit, FeatureTag
from ...database import getDB
from ...jobUtils import jobUpdated, commitTrigger, jobDeleted, getJobCachePath
from sqlalchemy.orm import Session

import Zoe.work
import Zoe.tasks

import os
import json
import re
import logging
logger = logging.getLogger(__name__)

import svn.remote as svn_remote

def available():
  return True

router = APIRouter(
  prefix="/vcs/svn",
  tags=["vcs/svn"],
  #dependencies=[Depends(get_token_header)],
  responses={404: {"description": "Not found"}},
)

branchRemoveRe = re.compile(r'^\/(?:trunk\/|(?:branches|tags)\/(?:[^/]+)\/)')

def getCommitFeatures(cm: SVNRepoCommit):
  db: Session = next(getDB())
  featureTagsDB = db.query(FeatureTag).all()
   
  regexps = []
  for ft in featureTagsDB:
    regexps.append([re.compile(ft.regexp.lower()), ft.output.lower()])
  detectedTags = {}
  for c in cm.changelist:
    type = c[0]
    path = c[1].lower()
    path = branchRemoveRe.sub('', path)
    for r in regexps:
      for m in r[0].findall(path):
        if isinstance(m, str):
          # fix for one match only
          m = [m]
        for i in range(0, len(m)):
          tag = r[1].replace('${}'.format(i + 1), m[i])
          detectedTags[tag] = True
  res = []
  for t in detectedTags:
    res.append(t)
  return cm, res
      


async def onPostCommitHook(data):
  repoName = data.get('repo', None)
  if repoName is None:
    logger.error("repo key missing in commit data: " + str(data))
    return

  revTrigger = data.get('rev', None)
  if revTrigger == '':
    revTrigger = None

  s = svn_remote.RemoteClient(
    '{}/{}'.format(getSVNSettings().svn_server_URL, repoName),
    username = getSVNSettings().svn_readonly_user,
    password = getSVNSettings().svn_readonly_pass,
    svn_filepath = '/usr/bin/svn')
  info = s.info(revision=revTrigger)
  #logger.info("INFO: " + str(info))

  db: Session = next(getDB())
  db.begin()
  r = db.query(SVNRepo).filter(SVNRepo.name == repoName).first()
  newEntry = False
  fromRev = 0
  if r is None:
    r = SVNRepo()
    newEntry = True
  else:
    fromRev = r.last_commit_revision
  r.uuid = info['repository/uuid']
  r.name = info['entry_path']
  r.last_commit_date = info['commit_date']
  r.last_commit_revision = int(info['commit_revision'])
  r.last_commit_author = info['commit_author']
  r.members = s.cat("members.txt").decode().strip().split('\n')[3:]
  if newEntry:
    db.add(r)

  #logger.debug(f'updating repo from revision {fromRev} to {r.last_commit_revision} ...')
  for e in s.log_default(None, None, None, None, None, fromRev, None, True, False):
    intRevision = int(e.revision)
    cm = db.query(SVNRepoCommit).filter(SVNRepoCommit.repo_name == repoName, SVNRepoCommit.revision == intRevision).first()
    if cm is None:
      cm = SVNRepoCommit()
      cm.id = '{}#{}'.format(r.name, intRevision)
      cm.repo_name = r.name
      cm.date = e.date
      cm.msg = e.msg
      cm.revision = intRevision
      cm.author = e.author
      changeList = e.changelist
      # now figure out branch
      branch = None
      for c in changeList:
        changeType = c[0]
        path = c[1].strip('/').split('/')
        if len(path) > 0:
          if path[0] == 'trunk':
            branch = 'trunk'
            break
          elif (path[0] == 'branches' or path[0] == 'tags') and len(path) > 1:
            branch = '/'.join(path[0:2])
            break

      cm.changelist = changeList
      cm.branch = branch
      db.add(cm)


    if revTrigger and cm.revision == int(revTrigger):
      
      # find any updates to job files first
      for c in cm.changelist:
        changeType = c[0]
        path = c[1]
        #logger.info(f' {changeType} ---- {path} ? {path.lower()[-7:]}')
        if path.lower()[-7:] == '.job.py':
          jobFilename = os.path.join(getJobCachePath(), 'svn', repoName, path.lstrip('/'))
          if changeType == 'A' or changeType == 'M':
            fileContent = s.cat(path).decode()
            os.makedirs(os.path.dirname(jobFilename), exist_ok=True)
            with open(jobFilename, "w") as f:
                f.write(fileContent)
            jobUpdated(jobFilename, cm)
          elif changeType == 'D':
            jobDeleted(jobFilename, cm)
          
      # trigger any jobs on the correct commit

      # manually convert the sql result object into a dict. Yes, this is the most safe but horrible approach ...
      cmDict = {
        "id": cm.id,
        "repo_name": cm.repo_name,
        "date": cm.date.isoformat(),
        "msg": cm.msg,
        "revision": cm.revision,
        "author": cm.author,
        "changeList": cm.changelist,
        "branch": cm.branch
      }
      await commitTrigger(cmDict)


  db.commit() # write the DB to disk

@router.post("/post-commit/")
async def post_commit(request: Request, background_tasks: BackgroundTasks):
  try:
    body = await request.body()
    # attention: assumes no binary files and all
    body = body.decode('utf8')
    data = json.loads(body, strict=False)

    # this is a hardcoded pre-shared key to pseudo authenticate the client
    if data.get('secret') != 'tRRSwN8ueat7ehR3hQw2B8tL':
      raise HTTPException(status_code=403)

    logger.info("POST-COMMIT: " + str(data))
    background_tasks.add_task(onPostCommitHook, data)
  except Exception as e:
    logger.error("POST-COMMIT - EXCEPTION: " + str(e))
    logger.error("POST-COMMIT - invalid post data: " + str(await request.body()))
  
  return {"message": "ok"}
