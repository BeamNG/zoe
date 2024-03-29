from sqlalchemy.orm import Session

import models


def get_platform(db:Session, platform_id: int):
    return db.query(models.Platform).filter(models.Platform.id == platform_id).first()
