import time
from typing import Annotated

import jwt
import requests
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

import models
from config import settings
from database import get_db

# TODO: create custom flow for oauth2
oauth2_scheme = OAuth2PasswordBearer("/auth/token", auto_error=False)


def exchange_discord_code(code: str) -> str:
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": "http://localhost:4200/accueil",
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(
        "https://discord.com/api/v10/oauth2/token",
        data=data,
        headers=headers,
        auth=(settings.discord_client_id, settings.discord_client_secret),
    )
    response.raise_for_status()
    return response.json()["access_token"]


def revoke_discord_token(token: str):
    data = {"token": token, "token_type_hint": "access_token"}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    requests.post(
        "https://discord.com/api/v10/oauth2/token/revoke",
        data=data,
        headers=headers,
        auth=(settings.discord_client_id, settings.discord_client_secret),
    )


def create_jwt(user_id: int, exp_time: int) -> str:
    payload = {"id": user_id, "exp": exp_time}
    return jwt.encode(payload, settings.secret_key, settings.algorithm)


def decode_jwt(token: str):
    try:
        payload = jwt.decode(token, settings.secret_key, settings.algorithm)
        if payload["exp"] < time.time():
            raise HTTPException(status_code=401, detail="Token expired")
        return payload["id"]
    except:
        raise HTTPException(status_code=401, detail="Invalid token")


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
