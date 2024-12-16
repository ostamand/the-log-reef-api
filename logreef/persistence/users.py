from datetime import datetime, timezone

from sqlalchemy.orm import Session
from sqlalchemy import text

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
    verified: bool = False,
) -> models.User:
    now = datetime.now(timezone.utc)

    db_user = models.User(
        username=username,
        hash_password=hash_password(password),
        email=email,
        fullname=fullname,
        is_admin=is_admin,
        is_demo=is_demo,
        force_login=False,
        created_on=now,
        last_login_on=now,
        verified=verified,
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


def authenticate(db: Session, username: str, password: str) -> models.User | bool:
    user = get_by_username(db, username)

    # try to get by email instead, could be smarter about this but will work
    if not user:
        user = get_by_email(db, username)

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
    force_login: bool | None = None,
) -> bool:
    updates = {}
    if last_login_on is not None:
        updates[models.User.last_login_on] = datetime.now(timezone.utc)
    if force_login is not None:
        updates[models.User.force_login] = force_login
    db.query(models.User).filter(models.User.id == user_id).update(updates)
    db.commit()
    return True


def set_to_verified(db: Session, email: str):
    sql = text("UPDATE users SET verified = TRUE WHERE email = :email")
    _ = db.execute(sql, {"email": email})
    db.commit()
    return True
