from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from api.config import get_config, ConfigAPI

db_url = get_config(ConfigAPI.DB_URL)

engine = create_engine(db_url)  # connect_args={"check_same_thread": False}

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def add_to_db(db: Session, model):
    db.add(model)
    db.commit()
    db.refresh(model)
    return model


def delete_from_db(db: Session, model):
    db.delete(model)
    db.commit()
