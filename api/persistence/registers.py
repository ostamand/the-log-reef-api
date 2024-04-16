from datetime import datetime

from api.persistence import models
from api.persistence.database import Session


def create(db: Session, data: models.RegisterAccessCode) -> models.RegisterAccessCode:
    db.add(data)
    db.commit()
    db.refresh(data)
    return data


def get_available_by_key(db: Session, key: str) -> models.RegisterAccessCode:
    return (
        db.query(models.RegisterAccessCode)
        .where(models.RegisterAccessCode.user_id == None)
        .where(models.RegisterAccessCode.key == key)
        .first()
    )


def get_by_key(db: Session, key: str) -> models.RegisterAccessCode:
    return (
        db.query(models.RegisterAccessCode)
        .where(models.RegisterAccessCode.key == key)
        .first()
    )


def update(db: Session, code_id: int, user_id: int, used_on: datetime):
    res = (
        db.query(models.RegisterAccessCode)
        .filter(models.RegisterAccessCode.id == code_id)
        .update(
            {
                models.RegisterAccessCode.used_on: used_on,
                models.RegisterAccessCode.user_id: user_id,
            }
        )
    )
    db.commit()
    return (
        db.query(models.RegisterAccessCode)
        .filter(models.RegisterAccessCode.id == code_id)
        .first()
    )
