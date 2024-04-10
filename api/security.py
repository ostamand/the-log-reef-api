from typing import Any

from datetime import datetime
from datetime import timedelta, timezone

from passlib.context import CryptContext
from jose import jwt

from api.config import get_config, ConfigAPI


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hash_password: str) -> bool:
    return pwd_context.verify(password, hash_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=get_config(ConfigAPI.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        get_config(ConfigAPI.SECRET_KEY),
        algorithm=get_config(ConfigAPI.ALGORITHM),
    )
    return encoded_jwt


def get_payload_from_token(token: str) -> dict[str, Any]:
    return jwt.decode(
        token,
        get_config(ConfigAPI.SECRET_KEY),
        algorithms=[get_config(ConfigAPI.ALGORITHM)],
    )
