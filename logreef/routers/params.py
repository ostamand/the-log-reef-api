from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from logreef import schemas
from logreef.persistence.database import get_session, Session
from logreef.user import get_current_user, check_for_demo
from logreef.persistence import params

router = APIRouter()


@router.post("")
def create_param(
    current_user: Annotated[schemas.User, Depends(get_current_user)],
    data: schemas.ParamCreate,
    db: Session = Depends(get_session),
    commit: bool = True,
):
    check_for_demo(current_user)
    return params.create(
        db,
        current_user.id,
        data.aquarium,
        data.param_type_name,
        data.value,
        test_kit=data.test_kit_name,
        timestamp=data.timestamp,
        commit=commit,
    )


@router.get("/")
def get_params(
    aquarium: str,
    current_user: Annotated[schemas.User, Depends(get_current_user)],
    type: str | None = None,
    days: int | None = None,
    limit: int | None = None,
    offset: int = 0,
    db: Session = Depends(get_session),
):
    return params.get_by_type(db, current_user.id, aquarium, type, days, limit, offset)


@router.get("/count")
def get_count(
    aquarium: str,
    current_user: Annotated[schemas.User, Depends(get_current_user)],
    type: str | None = None,
    days: int | None = None,
    db: Session = Depends(get_session),
):
    return params.get_count_by_type(db, current_user.id, aquarium, type, days)


@router.delete("/{param_id}")
def delete_param_by_id(
    param_id,
    current_user: Annotated[schemas.User, Depends(get_current_user)],
    db: Session = Depends(get_session),
):
    check_for_demo(current_user)
    try:
        deleted = params.delete_by_id(db, current_user.id, param_id)
    except:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail="Error while trying to delete parameter"
        )
    if not deleted:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Parameter does not exists, can't delete",
        )


@router.get("/{param_id}")
def get_param_by_id(
    param_id: int,
    current_user: Annotated[schemas.User, Depends(get_current_user)],
    db: Session = Depends(get_session),
):
    return params.get_param_by_id(db, current_user.id, param_id)


@router.put("/{param_id}")
def update_param_by_id(
    param_id: int,
    current_user: Annotated[schemas.User, Depends(get_current_user)],
    data: schemas.ParamUpdate,
    db: Session = Depends(get_session),
):
    check_for_demo(current_user)
    return params.update_by_id(db, current_user.id, param_id, **data.model_dump())
