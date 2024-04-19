from logreef.register import create_register_code, register_user, register_code_is_valid
from logreef.persistence import registers
from logreef.persistence.database import delete_from_db

from logreef.utils import get_random_string


def test_can_create_register_code(test_db):
    register_code = create_register_code(test_db)
    assert register_code.id
    assert register_code.key != ""
    assert register_code.created_on is not None
    assert register_code.used_on is None
    assert register_code.user_id is None
    delete_from_db(test_db, register_code)


def test_can_create_user_with_valid_key(test_db):
    register_code = create_register_code(test_db)

    username = get_random_string(10)
    password = get_random_string(10)

    ok, data = register_user(test_db, username, password, register_code.key)

    assert ok

    assert "user" in data
    user = data["user"]
    aquarium = data["aquarium"]
    assert user.username == username

    # check register code was used
    register_code_db = registers.get_by_key(test_db, register_code.key)
    assert register_code_db
    assert register_code_db.used_on is not None
    assert register_code_db.user_id == user.id

    delete_from_db(test_db, register_code)
    delete_from_db(test_db, user)


def test_register_code_not_valid(test_db):
    username = get_random_string(10)
    password = get_random_string(10)
    register_code = get_random_string(12)

    ok, data = register_user(test_db, username, password, register_code)

    assert not ok
    assert "detail" in data


def test_can_check_if_register_code_is_valid(test_db):
    not_valid = get_random_string(12)

    assert not register_code_is_valid(test_db, not_valid)

    register_code = create_register_code(test_db)

    assert register_code_is_valid(test_db, register_code.key)

    delete_from_db(test_db, register_code)
