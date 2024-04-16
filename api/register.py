from datetime import datetime
from datetime import UTC
from sqlalchemy.orm import Session

from api import schemas
from api.persistence import models, users
from api.utils import get_random_string
from api.persistence import registers

REGISTER_ACCESS_CODE_LENGTH = 12


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

    return True, {"user": user_db}
