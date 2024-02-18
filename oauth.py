import jwt
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

import models
from config import settings

# TODO: create custom flow for oauth2
oauth2_scheme = OAuth2PasswordBearer("/auth/token")


def create_jwt(user_id: int) -> str:
    payload = {"id": user_id}
    return jwt.encode(payload, settings.secret_key, settings.algorithm)


def decode_jwt(token: str) -> str:
    payload = jwt.decode(token, settings.secret_key, settings.algorithm)
    return payload["id"]


def is_user_actionneur(db: Session, user_id: int) -> bool:
    return db.query(models.Actionneur).get(user_id) is not None


def is_user_admin(db: Session, user_id: int) -> bool:
    user = db.query(models.Actionneur).get(user_id)
    return user is not None and user.is_admin
