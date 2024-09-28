from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from logreef import schemas
from logreef.user import get_current_user, check_for_demo
from logreef.persistence.database import Session, get_session
from logreef.persistence import aquariums

router = APIRouter()


@router.post("")
def create_aquarium(
    current_user: Annotated[schemas.User, Depends(get_current_user)],
    data: schemas.AquariumCreate,
    db: Session = Depends(get_session),
):
    check_for_demo(current_user)
    aquarium_db = aquariums.get_by_name(db, current_user.id, data.name)
    if aquarium_db is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Aquarium '{data.name}' already exists",
        )
    return aquariums.create(
        db, current_user.id, **data.model_dump()
    )


@router.get("")
def get_aquariums(
    current_user: Annotated[schemas.User, Depends(get_current_user)],
    db: Session = Depends(get_session),
):
    return aquariums.get_all(db, current_user.id)


@router.put("/{aquarium_id}")
def update_aquarium_by_id(
    aquarium_id: int,
    current_user: Annotated[schemas.User, Depends(get_current_user)],
    data: schemas.AquariumUpdate,
    db: Session = Depends(get_session),
):
    check_for_demo(current_user)
    return aquariums.update_by_id(db, aquarium_id, current_user.id, **data.model_dump())


@router.delete("/{aquarium_id}")
def delete_aquarium_by_id(
    aquarium_id,
    current_user: Annotated[schemas.User, Depends(get_current_user)],
    db: Session = Depends(get_session),
):
    check_for_demo(current_user)
    try:
        deleted = aquariums.delete_by_id(db, current_user.id, aquarium_id)
    except:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail="Error while trying to delete aquarium"
        )
    if not deleted:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Aquarium does not exists, can't delete",
        )
