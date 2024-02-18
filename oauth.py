from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

import models
from config import settings
from database import get_db

# TODO: create custom flow for oauth2
oauth2_scheme = OAuth2PasswordBearer("/auth/token", auto_error=False)


def create_jwt(user_id: int) -> str:
    payload = {"id": user_id}
    return jwt.encode(payload, settings.secret_key, settings.algorithm)


def decode_jwt(token: str) -> str:
    payload = jwt.decode(token, settings.secret_key, settings.algorithm)
    return payload["id"]


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        user_id = decode_jwt(token)
        if not user_id:
            raise HTTPException(status_code=401, detail="Unauthorized")
        return user_id
    except:
        raise HTTPException(status_code=401, detail="Unauthorized")


async def get_current_user_optional(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        user_id = decode_jwt(token)
        return user_id
    except:
        return None


async def get_current_actionneur(
    user_id: Annotated[int, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    user = db.query(models.Actionneur).get(user_id)
    if user is None:
        raise HTTPException(status_code=403, detail="Forbidden")
    return user


async def get_current_admin(user_id: Annotated[int, Depends(get_current_actionneur)]):
    if not user_id.is_admin:
        raise HTTPException(status_code=403, detail="Forbidden")
