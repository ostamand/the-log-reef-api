import pytest

from api.persistence.database import SessionLocal


@pytest.fixture()
def test_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
