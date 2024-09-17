from typing import Any
from datetime import datetime
from datetime import timedelta, timezone
import requests
from passlib.context import CryptContext
from jose import jwt

from logreef.config import get_config, ConfigAPI

SEND_EMAIL_URL = "https://thereeflog-function.azurewebsites.net/api/confirmation-email"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def send_confirmation_email(token) -> tuple[str, bool]:
    payload = {"token": token}
    headers = {"Content-Type": "application/json"}
    response = requests.post(SEND_EMAIL_URL, json=payload, headers=headers)
    return response.text, response.ok


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hash_password: str) -> bool:
    return pwd_context.verify(password, hash_password)


def create_access_token(
    data: dict, expires_delta: timedelta | None = None
) -> tuple[str, datetime]:
    to_encode = data.copy()
    if expires_delta is not None:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=float(get_config(ConfigAPI.ACCESS_TOKEN_EXPIRE_MINUTES))
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        get_config(ConfigAPI.SECRET_KEY),
        algorithm=get_config(ConfigAPI.ALGORITHM),
    )
    return encoded_jwt, expire


def create_email_confirmation_token(email: str):
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=float(get_config(ConfigAPI.ACCESS_TOKEN_EXPIRE_MINUTES))
    )
    to_encode = {"email": email, "exp": expire}
    return jwt.encode(
        to_encode,
        get_config(ConfigAPI.SECRET_KEY),
        algorithm=get_config(ConfigAPI.ALGORITHM),
    )


def get_payload_from_token(token: str) -> dict[str, Any]:
    return jwt.decode(
        token,
        get_config(ConfigAPI.SECRET_KEY),
        algorithms=[get_config(ConfigAPI.ALGORITHM)],
    )


def verify_email_token(token: str):
    try:
        payload = get_payload_from_token(token)
        email = payload.get("email")
        if email is None:
            raise Exception()
        return email, True
    except:
        return "", False
