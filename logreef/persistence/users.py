from datetime import datetime, timezone

from sqlalchemy.orm import Session
from sqlalchemy import text

from logreef.persistence import models
from logreef.security import hash_password, verify_password

def create(
    db: Session,
    username: str,
    password: str | None = None,
    email: str | None = None,
    fullname: str | None = None,
    is_demo: bool = False,
    is_admin: bool = False,
    verified: bool = False,
    google: bool = False,
    avatar_url: str | None = None
) -> models.User:
    now = datetime.now(timezone.utc)

    db_user = models.User(
        username=username,
        hash_password=hash_password(password) if password is not None else None,
        email=email,
        fullname=fullname,
        is_admin=is_admin,
        is_demo=is_demo,
        created_on=now,
        last_login_on=None if google else now, # not used for oauth login
        verified=verified,
        google=google,
        avatar_url=avatar_url
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def get_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_by_id(db: Session, id: int):
    return db.query(models.User).filter(models.User.id == id).first()


def get_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def authenticate(db: Session, email: str, password: str) -> models.User | bool:
    user = get_by_email(db, email)
    if not user:
        return False
    if not user.verified:
        return False
    if not verify_password(password, user.hash_password):
        return False
    return user


def update_by_id(
    db: Session,
    user_id: int,
    last_login_on: datetime | None = None,
) -> bool:
    updates = {}
    if last_login_on is not None:
        updates[models.User.last_login_on] = datetime.now(timezone.utc)
    db.query(models.User).filter(models.User.id == user_id).update(updates)
    db.commit()
    return True


def update_password(db: Session, user_id: int, new_password: str):
    hash_new_password  = hash_password(new_password)
    db.query(models.User).filter(models.User.id == user_id).update({models.User.hash_password: hash_new_password})
    db.commit()
    return True


def set_to_verified(db: Session, email: str):
    sql = text("UPDATE users SET verified = TRUE WHERE email = :email")
    _ = db.execute(sql, {"email": email})
    db.commit()
    return True
