import time
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db
from oauth import (
    create_jwt,
    decode_jwt,
    exchange_discord_code,
    oauth2_scheme,
    revoke_discord_token,
)
from utils import get_discord_user, get_discord_user_guilds

TOKEN_EXPIRATION_TIME = 3600 * 24
SERVER_HUB_GUILD_ID = 887850769011839006

router = APIRouter(prefix="/auth")


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
