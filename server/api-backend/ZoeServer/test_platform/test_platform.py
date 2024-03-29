from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

import ZoeServer.crud as crud
import ZoeServer.database as database
import ZoeServer.models as models



router = APIRouter(
    prefix="/platform",
    tags=["platform"],
    #dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)

@router.get("/platform/{platform_name}", tags=["platform"])
def read_platform(platform_id: int, db: Session = Depends(database.getDB)):
    return crud.get_platform(db , platform_id).name

@router.get("/platforms", tags=["platform"])
def all_platform(offset: int = 0, limit: int = 100, db: Session = Depends(database.getDB)):
    return db.query(models.Platform).offset(offset).limit(limit).all()

