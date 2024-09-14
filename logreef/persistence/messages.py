from datetime import datetime, timezone

from sqlalchemy.orm import Session

from logreef.persistence import models


def create(
    db: Session,
    email: str,
    message: str,
    source: str | None = None,
    user_id: int | None = None,
    full_name: str | None = None,
    subject: str | None = None,
):
    now = datetime.now(timezone.utc)

    db_message = models.Message(
        source=source,
        user_id=user_id,
        full_name=full_name,
        email=email,
        subject=subject,
        message=message,
        sent_on=now,
    )

    db.add(db_message)
    db.commit()
    db.refresh(db_message)

    return db_message
