import bcrypt
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db

router = APIRouter(prefix="/auth")


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


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


@router.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    query = db.query(models.User).filter(
        models.User.email == user.email or models.User.username == user.username
    )
    if query.first() is not None:
        raise HTTPException(status_code=400, detail="User already exists")

    user_dict = user.model_dump()
    user_dict["password_hash"] = _hash_password(user.password)
    user_dict["is_actionneur"] = False
    user_dict["is_admin"] = False
    del user_dict["password"]

    new_user = models.User(**user_dict)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
