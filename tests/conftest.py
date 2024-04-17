import pytest

from logreef.persistence.database import Database


@pytest.fixture()
def test_db():
    db = Database().get_session()
    try:
        yield db
    finally:
        db.close()
