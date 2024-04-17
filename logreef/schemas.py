from datetime import datetime

from pydantic import BaseModel


class Aquarium(BaseModel):
    id: int
    name: str
    started_on: datetime


class UserBase(BaseModel):
    username: str
    fullname: str | None = None
    email: str | None = None


class RegisterUser(UserBase):
    password: str
    register_access_code: str


class User(UserBase):
    id: int
    admin: bool

    class Config:
        from_attributes = True


class Me(User):
    aquariums: list[Aquarium]


class ParamCreate(BaseModel):
    test_kit_name: str | None = None
    param_type_name: str
    aquarium: int | str
    value: float
    timestamp: datetime | None = None


class AquariumCreate(BaseModel):
    name: str


class Token(BaseModel):
    access_token: str
    token_type: str
