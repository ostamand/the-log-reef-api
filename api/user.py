from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from api.security import get_payload_from_token
from api.persistence.database import get_db
from api.persistence import users, aquariums, models

from api import schemas

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = get_payload_from_token(token)
        username: str = payload.get("username")
        if username is None:
            raise credentials_exception
    except:
        raise credentials_exception
    user = users.get_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user


def get_me(db: Session, user: int | models.User) -> schemas.Me:
    if type(user) is int:
        user = users.get_by_id(db, user)

    user_aquariums = aquariums.get_all(db, user.id)

    all_aquariums = []
    for user_aquarium in user_aquariums:
        all_aquariums.append(
            schemas.Aquarium(
                id=user_aquarium.id,
                name=user_aquarium.name,
                started_on=user_aquarium.started_on,
            )
        )

    me = schemas.Me(
        id=user.id,
        username=user.username,
        admin=user.admin,
        aquariums=all_aquariums,
    )
    return me
