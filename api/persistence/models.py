from sqlalchemy import Integer, String, Boolean, ForeignKey, Numeric, DateTime
from sqlalchemy.orm import relationship, mapped_column, Mapped

from api.persistence.database import Base


class User(Base):
    __tablename__ = "users"

    id = mapped_column(Integer, primary_key=True)
    username = mapped_column(String, unique=True, index=True)
    hash_password = mapped_column(String)
    admin = mapped_column(Boolean)


class ParamType(Base):
    __tablename__ = "param_types"
    name = mapped_column(String, primary_key=True)
    unit = mapped_column(String, nullable=False)


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
    timestamp = mapped_column(DateTime, nullable=False)

    param_type: Mapped[ParamType] = relationship(
        "ParamType", foreign_keys="ParamValue.param_type_name"
    )  # lazy='joined'

    test_kit: Mapped[TestKit] = relationship(
        "TestKit", foreign_keys="ParamValue.test_kit_name"
    )  # lazy='joined'
