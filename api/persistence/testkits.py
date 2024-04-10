from api.persistence.database import Session
from api.persistence import models


def get_all_by_type(db: Session, param_type: str):
    return (
        db.query(models.TestKit)
        .where(models.TestKit.param_type_name == param_type)
        .all()
    )


def get_by_name(db: Session, test_kit_name: str):
    return db.query(models.TestKit).where(models.TestKit.name == test_kit_name).first()
