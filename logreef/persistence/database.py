from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, Session

from logreef.config import get_config, ConfigAPI

# db_url = get_config(ConfigAPI.DB_URL)

# engine = create_engine(db_url)  # connect_args={"check_same_thread": False}

# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = declarative_base()

# Base.metadata.create_all(bind=engine)
Base = declarative_base()


class Database:

    def __init__(self):
        self.db_url = get_config(ConfigAPI.DB_URL)
        self.engine = None
        self.session = None

    def get_session(self):
        if self.session is None:
            self.engine = self.get_engine()
            self.session = scoped_session(
                sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            )
        return self.session()

    def get_engine(self):
        if self.engine is None:
            self.engine = create_engine(self.db_url)
            Base.metadata.create_all(bind=self.engine)
        return self.engine


def get_db():
    db = Database().get_session()
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
