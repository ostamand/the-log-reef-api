from sqlalchemy.orm import Session

from logreef.persistence import models
from logreef.security import hash_password, verify_password


def create(
    db: Session,
    username: str,
    password: str,
    email: str | None = None,
    fullname: str | None = None,
    is_demo: bool = False,
    is_admin: bool = False,
) -> models.User:
    db_user = models.User(
        username=username,
        hash_password=hash_password(password),
        email=email,
        fullname=fullname,
        is_admin=is_admin,
        is_demo=is_demo,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_by_id(db: Session, id: int):
    return db.query(models.User).filter(models.User.id == id).first()


def authenticate(db: Session, username: str, password: str) -> models.User | bool:
    user = get_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hash_password):
        return False
    return user
