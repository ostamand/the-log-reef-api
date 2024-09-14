from datetime import datetime
from datetime import UTC
from sqlalchemy.orm import Session

from logreef.persistence import users, aquariums

DEFAULT_AQUARIUM_NAME = "Default"


def register_user(
    db: Session,
    username: str,
    password: str,
    fullname: str | None = None,
    email: str | None = None,
):
    user_db = users.create(db, username, password, email=email, fullname=fullname)

    if not user_db:
        return False, {"detail": "Can't create user"}

    # for now also create default aquarium for all new users
    default_aquarium = aquariums.create(db, user_db.id, DEFAULT_AQUARIUM_NAME)

    return True, {"user": user_db, "aquarium": default_aquarium}
