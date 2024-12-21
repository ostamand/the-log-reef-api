from sqlalchemy.orm import Session

from logreef.persistence import users, aquariums

DEFAULT_AQUARIUM_NAME = "Default"


def register_user(
    db: Session,
    username: str,
    password: str | None = None,
    fullname: str | None = None,
    email: str | None = None,
    google: bool = False,
    avatar_url: str | None = None
):
    try:
        user_db = users.create(
            db, 
            username, 
            password, 
            email=email, 
            fullname=fullname,
            google=google,
            avatar_url=avatar_url,
            verified=True if google else False
        )
    except Exception as ex:
        return False, {"detail": "Email already used."}

    # for now also create default aquarium for all new users
    default_aquarium = aquariums.create(db, user_db.id, DEFAULT_AQUARIUM_NAME)

    return True, {"user": user_db, "aquarium": default_aquarium}
