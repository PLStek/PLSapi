import time
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

import models
import schemas
from config import settings
from database import get_db
from discord_auth import (
    create_jwt,
    decode_jwt,
    exchange_discord_code,
    get_current_admin,
    oauth2_scheme,
    revoke_discord_token,
)
from utils import get_discord_user, get_discord_user_guilds

TOKEN_EXPIRATION_TIME = 3600 * 24
SERVER_HUB_GUILD_ID = 887850769011839006

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/token/", response_model=schemas.TokenData)
def discord_login(cred: schemas.TokenCreate):
    access_token = exchange_discord_code(cred)
    discord_user = get_discord_user(access_token)
    user_guilds: list[int] = get_discord_user_guilds(access_token)
    revoke_discord_token(access_token)

    if SERVER_HUB_GUILD_ID in user_guilds:
        exp_time = int(time.time()) + TOKEN_EXPIRATION_TIME
        jwt_token = create_jwt(discord_user.id, exp_time)
        return {"token": jwt_token, "exp_time": exp_time}
    else:
        raise HTTPException(
            status_code=401, detail="User isn't a member of the required guilds"
        )


@router.post("/token/bot/{id}", response_model=schemas.TokenData)
def discord_bot_login(
    id: str,
    admin: Annotated[models.Actionneur, Depends(get_current_admin)],
    db: Session = Depends(get_db),
):
    user = db.query(models.Actionneur).get(id)
    if not user or not user.is_admin:
        raise HTTPException(status_code=404, detail="User not found")

    exp_time = int(time.time()) + TOKEN_EXPIRATION_TIME
    jwt_token = create_jwt(user.id, exp_time)
    return {"token": jwt_token, "exp_time": exp_time}


@router.get("/me/", response_model=schemas.User)
def get_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)
):
    user_id = decode_jwt(token)
    user_data = {
        "id": user_id,
        "is_actionneur": False,
        "is_admin": False,
    }

    db_user = db.query(models.Actionneur).get(user_id)
    if db_user:
        user_data = {
            "id": user_id,
            "is_actionneur": True,
            "is_admin": db_user.is_admin,
        }
    return user_data


@router.get("/authorize/")
def redirect(redirect_uri: str):
    auth_uri = f"https://discord.com/oauth2/authorize?client_id={settings.discord_client_id}&response_type=code&redirect_uri={redirect_uri}&scope=identify+guilds"

    return RedirectResponse(url=auth_uri)
