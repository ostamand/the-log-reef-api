from .helpers import get_random_string

from logreef.persistence import users
from logreef.persistence import aquariums
from logreef.persistence.database import delete_from_db


def test_create_aquarium(test_db):
    username = get_random_string(10)
    password = get_random_string(10)
    aquarium_name = get_random_string(10)

    # create new test user
    user = users.create(test_db, username, password)
    assert user
    assert user.username == username

    # create aquarium for test user
    aquarium = aquariums.create(test_db, user.id, aquarium_name)

    assert aquarium is not None
    assert aquarium.name == aquarium_name
    assert aquarium.user_id == user.id

    # delete test user from db
    delete_from_db(test_db, user)

    # check if user still exists
    user_deleted = users.get_by_username(test_db, username)
    assert user_deleted is None

    # check if aquarium still exists
    aquarium_deleted = aquariums.get_by_name(test_db, user.id, aquarium_name)
    assert aquarium_deleted is None
