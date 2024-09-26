from .helpers import get_random_string, save_random_user_and_aquarium

from logreef.persistence import users
from logreef.persistence import aquariums
from logreef.persistence.database import delete_from_db


def test_get_by_username(test_db):
    user, aquarium = save_random_user_and_aquarium(test_db)

    user_aquariums = aquariums.get_by_user(test_db, user.id)

    assert len(user_aquariums) == 1
    assert user_aquariums[0].name == aquarium.name

    delete_from_db(test_db, user)


def test_create_aquarium(test_db):
    username = get_random_string(10)
    password = get_random_string(10)
    email = get_random_string(5) + "@" + get_random_string(3) + ".com"
    aquarium_name = get_random_string(10)

    # create new test user
    user = users.create(test_db, username, password, email=email)
    assert user
    assert user.username == username

    # create aquarium for test user
    test_description = "test"
    aquarium = aquariums.create(
        test_db, user.id, aquarium_name, description=test_description
    )

    assert aquarium is not None
    assert aquarium.name == aquarium_name
    assert aquarium.user_id == user.id
    assert aquarium.description == test_description

    # delete test user from db
    delete_from_db(test_db, user)

    # check if user still exists
    user_deleted = users.get_by_username(test_db, username)
    assert user_deleted is None

    # check if aquarium still exists
    aquarium_deleted = aquariums.get_by_name(test_db, user.id, aquarium_name)
    assert aquarium_deleted is None


def test_can_update_aquarium(test_db):
    user, aquarium = save_random_user_and_aquarium(test_db)

    description_updated = "description_updated"
    aquariums.update_by_id(
        test_db,
        aquarium.id,
        user.id,
        description=description_updated,
    )

    aquarium_updated = aquariums.get_by_name(test_db, user.id, aquarium.name)
    assert aquarium_updated is not None
    assert aquarium_updated.id == aquarium.id
    assert aquarium.description == description_updated
    assert aquarium_updated.updated_on > aquarium.created_on

    delete_from_db(test_db, user)
