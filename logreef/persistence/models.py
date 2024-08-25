from sqlalchemy import Integer, String, Boolean, ForeignKey, Numeric, DateTime
from sqlalchemy.orm import relationship, mapped_column, Mapped

from logreef.persistence.database import Base


class User(Base):
    __tablename__ = "users"

    id = mapped_column(Integer, primary_key=True)
    username = mapped_column(String, unique=True, index=True)
    fullname = mapped_column(String, nullable=True)
    email = mapped_column(String, nullable=True)
    hash_password = mapped_column(String)
    admin = mapped_column(Boolean)


class RegisterAccessCode(Base):
    __tablename__ = "register_access_codes"

    id = mapped_column(Integer, primary_key=True)
    user_id = mapped_column(Integer, ForeignKey(User.id), nullable=True)
    created_on = mapped_column(DateTime, nullable=True)
    used_on = mapped_column(DateTime, nullable=True)
    key = mapped_column(String, nullable=False, unique=True)


class ParamType(Base):
    __tablename__ = "param_types"
    name = mapped_column(String, primary_key=True)
    unit = mapped_column(String, nullable=False)
    display_name = mapped_column(String, nullable=False)


class TestKit(Base):
    __tablename__ = "test_kits"
    name = mapped_column(String, primary_key=True)
    param_type_name = mapped_column(String, ForeignKey(ParamType.name))
    display_name = mapped_column(String, nullable=False)
    display_unit = mapped_column(String, nullable=False)
    description = mapped_column(String, nullable=True)
    is_default = mapped_column(Boolean, default=False, nullable=False)

    param_type: Mapped[ParamType] = relationship(
        "ParamType", foreign_keys="TestKit.param_type_name"
    )


class Aquarium(Base):
    __tablename__ = "aquariums"

    id = mapped_column(Integer, primary_key=True)
    user_id = mapped_column(Integer, ForeignKey(User.id))
    name = mapped_column(String, nullable=False)
    started_on = mapped_column(DateTime)

    user: Mapped[User] = relationship("User", foreign_keys="Aquarium.user_id")


class ParamValue(Base):
    __tablename__ = "param_values"

    id = mapped_column(Integer, primary_key=True)
    user_id = mapped_column(Integer, ForeignKey(User.id))
    param_type_name = mapped_column(String, ForeignKey(ParamType.name))
    aquarium_id = mapped_column(Integer, ForeignKey(Aquarium.id))
    test_kit_name = mapped_column(String, ForeignKey(TestKit.name))
    value = mapped_column(Numeric, nullable=False)
    note = mapped_column(String, nullable=True)
    timestamp = mapped_column(DateTime, nullable=False)
    

    param_type: Mapped[ParamType] = relationship(
        "ParamType", foreign_keys="ParamValue.param_type_name"
    )  # lazy='joined'

    test_kit: Mapped[TestKit] = relationship(
        "TestKit", foreign_keys="ParamValue.test_kit_name"
    )  # lazy='joined'


class Units(Base):
    __tablename__ = "units"

    name = mapped_column(String, primary_key=True)
    display_name = mapped_column(String, nullable=False)


class Additives(Base):
    __tablename__ = "additives"

    name = mapped_column(String, primary_key=True)
    display_name = mapped_column(String, nullable=False)


class EventDosings(Base):
    __tablename__ = "event_dosings"

    id = mapped_column(Integer, primary_key=True)
    additive_name = mapped_column(String, ForeignKey(Additives.name))
    quantity = mapped_column(Numeric, nullable=True)
    description = mapped_column(String)
    unit_name = mapped_column(String, ForeignKey(Units.name))

    additive: Mapped[Additives] = relationship(
        "Additives", foreign_keys="EventDosings.additive_name"
    )
    unit: Mapped[Units] = relationship("Units", foreign_keys="EventDosings.unit_name")


class EventMiscs(Base):
    __tablename__ = "event_miscs"

    id = mapped_column(Integer, primary_key=True)
    description = mapped_column(String, nullable=False)


class EventWaterChanges(Base):
    __tablename__ = "event_water_changes"

    id = mapped_column(Integer, primary_key=True)
    quantity = mapped_column(Numeric, nullable=True)
    description = mapped_column(String)
    unit_name = mapped_column(String, ForeignKey(Units.name))

    unit: Mapped[Units] = relationship(
        "Units", foreign_keys="EventWaterChanges.unit_name"
    )


class Events(Base):
    __tablename__ = "events"

    id = mapped_column(Integer, primary_key=True)
    user_id = mapped_column(Integer, ForeignKey(User.id), nullable=True)
    aquarium_id = mapped_column(Integer, ForeignKey(Aquarium.id))
    dosing_id = mapped_column(Integer, ForeignKey(EventDosings.id))
    water_change_id = mapped_column(Integer, ForeignKey(EventWaterChanges.id))
    misc_id = mapped_column(Integer, ForeignKey(EventMiscs.id))
    timestamp = mapped_column(DateTime, nullable=False)

    dosing: Mapped[EventDosings] = relationship(
        "EventDosings", foreign_keys="Events.dosing_id"
    )
    water_change: Mapped[EventWaterChanges] = relationship(
        "EventWaterChanges", foreign_keys="Events.water_change_id"
    )
    misc: Mapped[EventMiscs] = relationship("EventMiscs", foreign_keys="Events.misc_id")
