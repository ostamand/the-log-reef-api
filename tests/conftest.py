import pytest

from logreef.persistence.database import get_scoped_session


@pytest.fixture()
def test_db():
    Session = get_scoped_session()
    session = Session()
    try:
        yield session
    finally:
        Session.remove()
