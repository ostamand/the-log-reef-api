from datetime import datetime

from pydantic import BaseModel

from logreef.persistence import models


class Aquarium(BaseModel):
    id: int
    name: str


class UserBase(BaseModel):
    username: str
    fullname: str | None = None
    email: str | None = None


class RegisterUser(UserBase):
    password: str
    register_access_code: str


class User(UserBase):
    id: int
    is_admin: bool
    is_demo: bool
    created_on: datetime

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


class ParamInfo(BaseModel):
    id: int
    param_type_name: str
    param_type_display_name: str
    test_kit_name: str
    test_kit_display_name: str
    value: float
    unit: str
    note: str | None
    timestamp: datetime
    created_on: datetime
    updated_on: datetime

    @classmethod
    def get_fields(cls):
        return [
            "id",
            "param_type_name",
            "param_type_display_name",
            "test_kit_name",
            "test_kit_display_name",
            "value",
            "unit",
            "timestamp",
            "note",
            "created_on",
            "updated_on",
        ]


class ParamUpdate(BaseModel):
    value: float | None = None
    note: str | None = None


class WaterChangeCreate(BaseModel):
    aquarium: int | str
    unit_name: str
    quantity: float | None = None
    description: str | None = None
    timestamp: datetime | None = None


class Unit(BaseModel):
    name: str
    display_name: str


class WaterChange(BaseModel):
    quantity: float | None
    description: str | None
    unit: Unit


class EventWaterChange(BaseModel):
    id: int
    water_change_id: int
    timestamp: datetime
    detail: WaterChange

    @staticmethod
    def convert(data: models.Events):
        return EventWaterChange(
            id=data.id,
            water_change_id=data.water_change_id,
            timestamp=data.timestamp,
            detail=WaterChange(
                quantity=data.water_change.quantity,
                description=data.water_change.description,
                unit=Unit(
                    name=data.water_change.unit.name,
                    display_name=data.water_change.unit.display_name,
                ),
            ),
        )


class AquariumCreate(BaseModel):
    name: str


class Token(BaseModel):
    access_token: str
    token_type: str
    is_demo: bool
    is_admin: bool
