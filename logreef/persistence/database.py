from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, Session

from logreef.config import get_config, ConfigAPI


Base = declarative_base()


def get_scoped_session(db_url=None):
    db_url =  db_url if db_url is not None else get_config(ConfigAPI.DB_URL)
    engine = create_engine(db_url)
    Session = scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=engine)
    )
    return Session


def get_session():
    Session = get_scoped_session()
    try:
        session = Session()
        yield session
    except Exception as e:
        session.rollback()
        raise e
    finally:
        Session.remove()
        #session.close()


def add_to_db(session: Session, model):
    session.add(model)
    session.commit()
    session.refresh(model)
    return model


def delete_from_db(session: Session, model):
    session.delete(model)
    session.commit()
