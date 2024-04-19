import datetime

from sqlalchemy.orm import Session
from sqlalchemy import select

from logreef.persistence import models
from logreef.persistence.database import add_to_db


def create(
    db: Session, user_id: int, name: str, started_on: datetime = None
) -> models.Aquarium:
    if started_on is None:
        started_on = datetime.datetime.now(datetime.UTC)
    db_aquarium = models.Aquarium(user_id=user_id, name=name, started_on=started_on)
    add_to_db(db, db_aquarium)
    return db_aquarium


def get_by_name(db: Session, user_id: int, name: str):
    return (
        db.query(models.Aquarium)
        .filter(models.Aquarium.user_id == user_id)
        .filter(models.Aquarium.name == name)
        .first()
    )


def get_by_user(db: Session, user_id: int) -> list[models.Aquarium]:
    result = db.execute(
        select(models.Aquarium).where(models.Aquarium.user_id == user_id)
    )
    return [row[0] for row in result]


def get_all(db: Session, user_id: int) -> list[models.Aquarium]:
    return db.query(models.Aquarium).filter(models.Aquarium.user_id == user_id).all()
