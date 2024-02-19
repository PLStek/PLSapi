from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db
from oauth import get_current_admin

router = APIRouter(prefix="/actionneurs")


@router.get("/", response_model=List[schemas.Actionneur])
def get_actionneurs(db: Session = Depends(get_db)):
    try:
        query = db.query(models.Actionneur)
        return query.all()
    except DBAPIError:
        raise HTTPException(status_code=500, detail="Database error")


@router.post("/", response_model=schemas.User, status_code=201)
def add_actionneur(
    user: schemas.Actionneur,
    admin: Annotated[models.Actionneur, Depends(get_current_admin)],
    db: Session = Depends(get_db),
):
    try:
        new_user = models.User(**user.model_dump())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except DBAPIError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")
