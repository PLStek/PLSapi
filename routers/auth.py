import bcrypt
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db

router = APIRouter(prefix="/auth")


@router.post("/login", response_model=schemas.User)
def login(login_info: schemas.UserLogin, db: Session = Depends(get_db)):
    query = db.query(models.User).filter(
        models.User.email == login_info.login
        or models.User.username == login_info.login
    )
    user = query.first()

    if user is None:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not bcrypt.checkpw(
        login_info.password.encode("utf-8"), user.password_hash.encode("utf-8")
    ):
        raise HTTPException(status_code=400, detail="Invalid password")

    return user
