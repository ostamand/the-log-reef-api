from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, Session

from logreef.config import get_config, ConfigAPI

engine = create_engine(get_config(ConfigAPI.DB_URL))
SessionLocal= scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)
Base = declarative_base()


def get_session():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise e
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
