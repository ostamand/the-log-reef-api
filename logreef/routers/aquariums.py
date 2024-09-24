from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Response

from logreef import schemas
from logreef.user import get_current_user, check_for_force_login, check_for_demo
from logreef.persistence.database import Session, get_session
from logreef.persistence import aquariums

router = APIRouter()


@router.post("/aquariums")
def create_aquarium(
    current_user: Annotated[schemas.User, Depends(get_current_user)],
    data: schemas.AquariumCreate,
    db: Session = Depends(get_session),
):
    check_for_force_login(current_user)
    check_for_demo(current_user)
    aquarium_db = aquariums.get_by_name(db, current_user.id, data.name)
    if aquarium_db is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Aquarium '{data.name}' already exists",
        )
    return aquariums.create(db, current_user.id, data.name)


@router.get("/")
def get_aquariums(
    current_user: Annotated[schemas.User, Depends(get_current_user)],
    db: Session = Depends(get_session),
):
    check_for_force_login(current_user)
    return aquariums.get_all(db, current_user.id)


@router.put("/")
def update_aquarium_by_id(
    name: str,
    current_user: Annotated[schemas.User, Depends(get_current_user)],
    data: schemas.AquariumUpdate,
    db: Session = Depends(get_session),
):
    aquariums.update_by_name(db, name, current_user.id, **data.model_dump())
    return Response(status_code=status.HTTP_200_OK)
