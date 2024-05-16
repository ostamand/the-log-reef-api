from datetime import datetime, timezone, timedelta

from sqlalchemy.orm import Session

from logreef.persistence import models


def get_water_changed(
    db: Session, user_id: int, aquarium_id: int, days: int | None = None
):
    raw_query = db.query(models.Events).where(models.Events.user_id == user_id).where(
        models.Events.aquarium_id == aquarium_id
    ).where(models.Events.water_change_id is not None)

    if days is not None and days > 0:
        ts = datetime.now(timezone.utc) - timedelta(days=days)
        raw_query = raw_query.where(models.Events.timestamp > ts)
    
    raw_query = raw_query.order_by(models.Events.timestamp.desc())

    return raw_query.all()


def create_water_change(
    db: Session,
    user_id: int,
    aquarium_id: int,
    quantity: float,
    unit_name: str,
    description: str,
    timestamp: datetime | None = None,
):
    if not timestamp:
        timestamp = datetime.now(timezone.utc)

    db_water_change = models.EventWaterChanges(
        quantity=quantity, description=description, unit_name=unit_name
    )

    db_event = models.Events(
        user_id=user_id,
        aquarium_id=aquarium_id,
        water_change=db_water_change,
        timestamp=timestamp,
    )

    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    return db_event
