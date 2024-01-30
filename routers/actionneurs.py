from enum import Enum
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

import models
import schemas
from database import get_db

router = APIRouter(prefix="/actionneurs")


@router.get("/", response_model=List[schemas.User])
def get_actionneurs(db: Session = Depends(get_db)):
    query = db.query(models.User).filter(models.User.is_actionneur == True)
    return query.all()
