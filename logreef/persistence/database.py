from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, Session

from logreef.config import get_config, ConfigAPI


Base = declarative_base()


class Database:

    def __init__(self, db_url: str | None = None):
        self.db_url = get_config(ConfigAPI.DB_URL) if db_url is None else db_url
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


def get_session():
    session = Database().get_session()
    try:
        yield session
    finally:
        session.close()


def add_to_db(session: Session, model):
    session.add(model)
    session.commit()
    session.refresh(model)
    return model


def delete_from_db(session: Session, model):
    session.delete(model)
    session.commit()
