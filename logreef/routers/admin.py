from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from logreef.user import get_current_user
from logreef import schemas
from logreef.persistence.database import get_session, Session


router = APIRouter()


def check_for_admin(user: schemas.User):
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Need admin credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/backup-user")
def backup_user(
    current_user: Annotated[schemas.User, Depends(get_current_user)],
    username: str,
    db: Session = Depends(get_session),
):
    check_for_admin(current_user)
    return current_user
