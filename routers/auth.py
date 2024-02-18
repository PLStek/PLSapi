from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db
from oauth import create_jwt, decode_jwt, get_current_user, oauth2_scheme
from utils import get_discord_user, get_discord_user_guilds

SERVER_HUB_GUILD_ID = 887850769011839006

router = APIRouter(prefix="/auth")


@router.post("/token")
def discord_login(token: str):
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
