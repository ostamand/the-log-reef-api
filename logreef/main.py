from typing import Annotated
import logging
from datetime import datetime, timezone

from fastapi import FastAPI, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from logreef import schemas, __version__
from logreef.persistence import users, testkits, events, messages
from logreef.user import get_current_user, get_me
from logreef import summary
from logreef.persistence.database import get_session
from logreef.security import (
    create_access_token,
    verify_email_token,
    create_email_confirmation_token,
    send_confirmation_email,
    get_payload_from_supabase_token
)
from logreef.user import get_current_user, get_me
from logreef.register import register_user
from logreef.routers import admin, params, aquariums
from logreef.config import ConfigAPI, get_config

load_dotenv()

logging.getLogger("passlib").setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(admin.router, prefix="/admin")
app.include_router(params.router, prefix="/params")
app.include_router(aquariums.router, prefix="/aquariums")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"api": "logreef", "version": __version__, "db": get_config(ConfigAPI.DB_URL)}


@app.get("/users/me", response_model=schemas.Me)
async def read_users_me(
    current_user: Annotated[schemas.User, Depends(get_current_user)],
    db: Session = Depends(get_session),
):
    return get_me(db, current_user)


@app.get("/register")
def check_for_new_user(username: str, email: str, db: Session = Depends(get_session)):
    user = users.get_by_email(db, email)
    if user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists."
        )
    user = users.get_by_username(db, username)
    if user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists, select a different one.",
        )
    return {"detail": "Email and username are valid"}


@app.post("/register") # , response_model=schemas.User
def create_new_user(req: schemas.RegisterUser, db: Session = Depends(get_session)):
    # check if should register thru oauth 2 access token
    if req.accessToken is not None:
        try:
            user_data = get_payload_from_supabase_token(req.accessToken)
        except:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Access token is not valid")
        
        # register user
        ok, data = register_user(
            db,
            username=user_data["user_metadata"]["name"],
            password=None,
            email=user_data["user_metadata"]["email"],
            fullname=user_data["user_metadata"]["full_name"],
            avatar_url=user_data["user_metadata"]["avatar_url"],
            google=True
        )

        if not ok:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=data["detail"])

        return user_data

    ok, data = register_user(
        db,
        username=req.username,
        password=req.password,
        email=req.email,
        fullname=req.fullname,
    )

    if not ok:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=data["detail"])

    # send email confirmation email
    try:
        # get register token
        email_token = create_email_confirmation_token(req.email)

        # send confirmation email with token
        _, ok = send_confirmation_email(email_token)

        if not ok:
            raise Exception()

    except Exception as ex:
        # TODO delete user from db
        logger.error(ex)
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not send confirmation email, please try again.",
        )

    return data["user"]


@app.get("/confirm-email")
def confirm_email(token: str, db: Session = Depends(get_session)):
    email, ok = verify_email_token(token)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Confirmation email token is not valid",
        )
    ok = users.set_to_verified(db, email)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Confirmation failed, try again",
        )
    return {"detail": "User email confirmed", "email": email}


@app.post("/messages")
def save_message(
    data: schemas.MessageCreate,
    db: Session = Depends(get_session),
):
    return messages.create(
        db,
        data.email,
        data.message,
        source=data.source,
        user_id=data.user_id,
        full_name=data.full_name,
        subject=data.subject,
    )


@app.post("/login")
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_session),
) -> schemas.Token:
    user = users.authenticate(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username, password or account not verified",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_updates = {}

    # update last login time
    if not user.is_demo:
        user_updates["last_login_on"] = datetime.now(timezone.utc)

    if user_updates:
        users.update_by_id(db, user.id, **user_updates)

    access_token, expires_date = create_access_token(data={"username": user.username})

    return schemas.Token(
        username=user.username,
        email=user.email,
        access_token=access_token,
        token_type="bearer",
        expires_on=expires_date,
        is_demo=user.is_demo,
        is_admin=user.is_admin,
    )


@app.get("/summary/")
def get_summary(
    aquarium: str,
    current_user: Annotated[schemas.User, Depends(get_current_user)],
    db: Session = Depends(get_session),
    type: str | None = None,
):
    if type is not None:
        return {type: summary.get_by_type(db, current_user.id, aquarium, type)}
    return summary.get_for_all(db, current_user.id, aquarium)


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


@app.post("/events/waterchange", response_model=schemas.EventWaterChange)
def create_water_change(
    current_user: Annotated[schemas.User, Depends(get_current_user)],
    data: schemas.WaterChangeCreate,
    db: Session = Depends(get_session),
):
    event_db = events.create_water_change(
        db,
        current_user.id,
        data.aquarium,
        data.unit_name,
        data.quantity,
        data.description,
        data.timestamp,
    )
    return schemas.EventWaterChange.convert(event_db)


@app.get("/events/waterchange/")
def get_water_changes(
    current_user: Annotated[schemas.User, Depends(get_current_user)],
    db: Session = Depends(get_session),
    days: int | None = None,
):
    water_changes_db = events.get_water_changes(db, current_user.id, days=days)
    return list(map(lambda x: schemas.EventWaterChange.convert(x), water_changes_db))
