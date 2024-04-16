from datetime import datetime
from datetime import UTC
from sqlalchemy.orm import Session

from api.persistence import models, users, aquariums
from api.utils import get_random_string
from api.persistence import registers

REGISTER_ACCESS_CODE_LENGTH = 12
DEFAULT_AQUARIUM_NAME = "Default"


def register_code_is_valid(db: Session, register_code: str):
    access_code_db = registers.get_available_by_key(db, register_code)
    return access_code_db is not None


def create_register_code(db: Session) -> models.RegisterAccessCode:
    register_code = models.RegisterAccessCode(
        created_on=datetime.now(UTC), key=get_random_string(REGISTER_ACCESS_CODE_LENGTH)
    )
    return registers.create(db, register_code)


def register_user(db: Session, username: str, password: str, register_code: str):
    # check register access token
    if len(register_code) != REGISTER_ACCESS_CODE_LENGTH:
        return False, {"detail": "Wrong access code"}
    access_code_db = registers.get_available_by_key(db, register_code)
    if access_code_db is None:
        return False, {"detail": "Access code already used or not available"}

    user_db = users.create(db, username, password)
    if not user_db:
        return False, {"detail": "Can't create user"}

    registers.update(db, access_code_db.id, user_db.id, datetime.now(UTC))

    # for now also create default aquarium for all new users
    default_aquarium = aquariums.create(db, user_db.id, DEFAULT_AQUARIUM_NAME)

    return True, {"user": user_db, "aquarium": default_aquarium}
