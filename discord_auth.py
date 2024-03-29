import time
from typing import Annotated

import jwt
import requests
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

import models
import schemas
from config import settings
from database import get_db

ALGORITHM = "HS256"

# TODO: create custom flow for oauth2
oauth2_scheme = OAuth2PasswordBearer("/auth/token", auto_error=False)


def exchange_discord_code(cred: schemas.TokenCreate) -> str:
    data = {
        "grant_type": "authorization_code",
        "code": cred.code,
        "redirect_uri": cred.redirect_uri,
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
    return jwt.encode(payload, settings.token_secret, ALGORITHM)


def decode_jwt(token: str) -> int:
    try:
        payload = jwt.decode(token, settings.token_secret, ALGORITHM)
        if payload["exp"] < time.time() or not payload["id"]:
            raise HTTPException(status_code=401, detail="Invalid token")
        return payload["id"]
    except:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        return decode_jwt(token)
    except:
        return None


async def get_current_actionneur(
    token: Annotated[int, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
):
    user_id = decode_jwt(token)
    user = db.query(models.Actionneur).get(user_id)
    if user is None:
        raise HTTPException(
            status_code=403, detail="You need to be an actionneur to access this."
        )
    return user


async def get_current_admin(user: Annotated[int, Depends(get_current_actionneur)]):
    if not user.is_admin:
        raise HTTPException(
            status_code=403, detail="You need to be an admin to access this."
        )

    return user
