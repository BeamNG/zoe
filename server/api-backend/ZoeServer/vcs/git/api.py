from fastapi import APIRouter, BackgroundTasks, Request

import json
import logging
logger = logging.getLogger(__name__)

def available():
    return True

router = APIRouter(
    prefix="/vcs/git",
    tags=["vcs/git"],
    #dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)

@router.post("/push/")
async def post_commit(request: Request, background_tasks: BackgroundTasks):
  try:
    body = await request.body()
    # attention: assumes no binary files and all
    body = body.decode('utf8')
    data = json.loads(body, strict=False)

    # this is a hardcoded pre-shared key to pseudo authenticate the client
    #if data.get('secret') != 'tRRSwN8ueat7ehR3hQw2B8tL':
    #  raise HTTPException(status_code=403)

    logger.info("PUSH: " + str(data))
    #background_tasks.add_task(onPostCommitHook, data)
  except Exception as e:
    logger.error("PUSH - EXCEPTION: " + str(e))
    logger.error("PUSH - invalid post data: " + str(await request.body()))
