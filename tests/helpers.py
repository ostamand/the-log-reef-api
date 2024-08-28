import string
import random

from logreef.persistence import users, models, aquariums
from logreef.persistence.database import Session
from logreef.config import get_config, ConfigAPI


def get_user(db: Session) -> models.User:
    user = users.get_by_username(db, get_config(ConfigAPI.TEST_USERNAME))
    assert user is not None
    assert user.username == get_config(ConfigAPI.TEST_USERNAME)
    return user


def get_random_string(length: int):
    return "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(length)
    )


def save_random_user(db: Session, is_demo=False) -> models.User:
    username = get_random_string(10)
    password = get_random_string(10)
    # create new test user
    user = users.create(db, username, password, is_demo=is_demo)
    return user


def save_random_aquarium(db: Session, user_id: int) -> models.Aquarium:
    name = get_random_string(10)
    return aquariums.create(db, user_id, name)


def save_random_user_and_aquarium(
    db: Session, is_demo: bool = False
) -> tuple[models.User, models.Aquarium]:
    user = save_random_user(db, is_demo=is_demo)
    aquarium = save_random_aquarium(db, user.id)
    return user, aquarium
