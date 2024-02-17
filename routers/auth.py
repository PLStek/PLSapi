import bcrypt
import jwt
import requests
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

import models
import schemas
from config import settings
from database import get_db

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


@router.post("/discord")
def discord_login(token: str, db: Session = Depends(get_db)):
    data = {"Authorization": f"Bearer {token}"}
    response = requests.get("https://discord.com/api/users/@me/guilds", headers=data)
    res = response.json()
    filtered_res = list(filter(lambda x: x["id"] == "887850769011839006", res))

    if filtered_res:
        payload = {"discord_token": token}
        jwt_token = jwt.encode(payload, settings.secret_key, settings.algorithm)
        return {"token": jwt_token}
