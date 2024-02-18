from typing import Annotated

import bcrypt
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db
from oauth import create_jwt, decode_jwt, oauth2_scheme
from utils import get_discord_user, get_discord_user_guilds

SERVER_HUB_GUILD_ID = 887850769011839006

router = APIRouter(prefix="/auth")


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


@router.post("/login", response_model=schemas.User)
def login(login_info: schemas.UserLogin, db: Session = Depends(get_db)):
    try:
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
    except DBAPIError:
        raise HTTPException(status_code=500, detail="Database error")


@router.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
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
    except DBAPIError:
        raise HTTPException(status_code=500, detail="Database error")


@router.put("/change_password/{id}", response_model=schemas.User)
def change_password(
    id: int, body: schemas.UserChangePassword, db: Session = Depends(get_db)
):
    try:
        query = db.query(models.User).filter_by(id=id)
        user = query.first()

        if user is None:
            raise HTTPException(status_code=400, detail="User doesn't exist")

        if not bcrypt.checkpw(
            body.password.encode("utf-8"), user.password_hash.encode("utf-8")
        ):
            raise HTTPException(status_code=400, detail="Invalid password")

        password_hash = _hash_password(body.new_password)

        query.update({"password_hash": password_hash})
        db.commit()
        return user
    except DBAPIError:
        raise HTTPException(status_code=500, detail="Database error")


@router.post("/token")
def discord_login(token: str, db: Session = Depends(get_db)):
    user_guilds: list[int] = get_discord_user_guilds(token)

    if SERVER_HUB_GUILD_ID in user_guilds:
        discord_user = get_discord_user(token)

        jwt_token = create_jwt(discord_user.id)
        return {"token": jwt_token}
    else:
        raise HTTPException(status_code=401, detail="Unauthorized")


@router.get("/me", response_model=schemas.User)
def get_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)
):
    user_id = decode_jwt(token)
    user_data = {
        "username": None,
        "is_actionneur": False,
        "is_admin": False,
    }

    db_user = db.query(models.Actionneur).get(user_id)
    if db_user:
        user_data = {
            "username": db_user.username,
            "is_actionneur": True,
            "is_admin": db_user.is_admin,
        }

    return user_data
