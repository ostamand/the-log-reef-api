from typing import Annotated
import logging

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from logreef import schemas, __version__
from logreef.persistence import users, params, aquariums, testkits
from logreef import summary
from logreef.persistence.database import get_session
from logreef.security import create_access_token
from logreef.user import get_current_user, get_me
from logreef.register import register_user, register_code_is_valid

logging.getLogger("passlib").setLevel(logging.ERROR)


app = FastAPI()


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"api": "logreef", "version": __version__}


@app.get("/users/me", response_model=schemas.Me)
async def read_users_me(
    current_user: Annotated[schemas.User, Depends(get_current_user)],
    db: Session = Depends(get_session),
):
    return get_me(db, current_user)


@app.post("/register", response_model=schemas.User)
def create_user_with_code(
    userData: schemas.RegisterUser, db: Session = Depends(get_session)
):
    ok, data = register_user(
        db,
        username=userData.username,
        password=userData.password,
        register_code=userData.register_access_code,
        email=userData.email,
        fullname=userData.fullname,
    )
    if not ok:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=data["detail"])
    return data["user"]


@app.get("/register")
def check_register(code: str | None = None, db: Session = Depends(get_session)):
    response = {}
    if code is not None:
        if register_code_is_valid(db, code):
            response["code"] = True
        else:
            response["code"] = False
    return response


@app.post("/aquariums")
def create_aquarium(
    current_user: Annotated[schemas.User, Depends(get_current_user)],
    aquariumCreate: schemas.AquariumCreate,
    db: Session = Depends(get_session),
):
    aquarium_db = aquariums.get_by_name(db, current_user.id, aquariumCreate.name)
    if aquarium_db is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Aquarium '{aquariumCreate.name}' already exists",
        )
    return aquariums.create(db, current_user.id, aquariumCreate.name)


@app.get("/aquariums")
def get_aquariums(
    current_user: Annotated[schemas.User, Depends(get_current_user)],
    db: Session = Depends(get_session),
):
    return aquariums.get_all(db, current_user.id)


@app.post("/login")
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_session),
) -> schemas.Token:
    user = users.authenticate(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"username": user.username})
    return schemas.Token(access_token=access_token, token_type="bearer")


@app.post("/params")
def create_param(
    current_user: Annotated[schemas.User, Depends(get_current_user)],
    paramCreate: schemas.ParamCreate,
    db: Session = Depends(get_session),
    commit: bool = True,
):
    # TODO: unit conversion
    # TODO: add optional time to data
    return params.create(
        db,
        current_user.id,
        paramCreate.aquarium,
        paramCreate.param_type_name,
        paramCreate.value,
        test_kit=paramCreate.test_kit_name,
        timestamp=paramCreate.timestamp,
        commit=commit,
    )


@app.get("/params/")
def get_params(
    current_user: Annotated[schemas.User, Depends(get_current_user)],
    db: Session = Depends(get_session),
    type: str | None = None,
    days: int | None = None,
    limit: int | None = None,
    offset: int = 0,
):
    return params.get_by_type(db, current_user.id, type, days, limit, offset)


@app.delete("/params/{param_id}")
def delete_param_by_id(
    param_id,
    current_user: Annotated[schemas.User, Depends(get_current_user)],
    db: Session = Depends(get_session),
):
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


@app.get("/params/{param_id}")
def get_param_by_id(
    param_id: int,
    current_user: Annotated[schemas.User, Depends(get_current_user)],
):
    return params.get_info_by_id(current_user.id, param_id)


@app.put("/params/{param_id}")
def update_param_by_id(
    param_id: int,
    value: float,
    current_user: Annotated[schemas.User, Depends(get_current_user)],
    db: Session = Depends(get_session),
):
    return params.update_by_id(db, current_user.id, param_id, value)


@app.get("/summary/")
def get_summary(
    current_user: Annotated[schemas.User, Depends(get_current_user)],
    db: Session = Depends(get_session),
    type: str | None = None,
):
    if type is not None:
        return {type: summary.get_by_type(db, current_user.id, type)}
    return summary.get_for_all(db, current_user.id)


@app.get("/testkits/")
def get_test_kits(
    type: str | None = None,
    name: str | None = None,
    db: Session = Depends(get_session),
):
    if type is not None and name is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Use either 'type' or 'name'",
        )
    if type is not None:
        return testkits.get_all_by_type(db, type)
    elif name is not None:
        return testkits.get_by_name(db, name)
