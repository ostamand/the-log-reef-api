import pytest
import math

from logreef.persistence import params
from logreef.persistence.database import delete_from_db
from logreef.config import TestKits, ParamTypes

from .helpers import save_random_user, save_random_aquarium


def test_create_value(test_db):
    user = save_random_user(test_db)
    aquarium = save_random_aquarium(test_db, user.id)

    value = 8.4
    param_type = "ph"

    paramValue = params.create(test_db, user.id, aquarium.name, param_type, value)

    pytest.approx(paramValue.value, value)
    assert paramValue.param_type.name == param_type

    delete_from_db(test_db, paramValue)

    latestValue = params.get_by_type(test_db, user.id, param_type, 1)

    assert len(latestValue) == 0

    delete_from_db(test_db, user)


def test_can_get_param_type(test_db):
    param_type_name = "ph"
    param_type = params.get_type(test_db, param_type_name)
    assert param_type
    assert param_type.name == param_type_name


def test_can_get_param_by_type(test_db):
    user = save_random_user(test_db)
    aquarium = save_random_aquarium(test_db, user.id)

    param_1 = params.create(test_db, user.id, aquarium.name, "ph", 1.0)
    param_2 = params.create(
        test_db,
        user.id,
        aquarium.name,
        "alkalinity",
        2.0,
    )
    param_3 = params.create(
        test_db,
        user.id,
        aquarium.name,
        "alkalinity",
        3.0,
    )

    values = params.get_by_type(test_db, user.id, "ph")
    assert len(values) == 1

    values = params.get_by_type(test_db, user.id, "alkalinity")
    assert len(values) == 2

    delete_from_db(test_db, user)


def test_can_filter_by_user(test_db):
    user_1 = save_random_user(test_db)
    aquarium_1 = save_random_aquarium(test_db, user_1.id)

    param_1 = params.create(test_db, user_1.id, aquarium_1.name, "ph", 1.0)

    user_2 = save_random_user(test_db)
    aquarium_2 = save_random_aquarium(test_db, user_2.id)

    param_2 = params.create(
        test_db,
        user_2.id,
        aquarium_2.name,
        "alkalinity",
        10.0,
    )

    values = params.get_by_type(test_db, user_2.id, "ph")
    assert len(values) == 0

    values = params.get_by_type(test_db, user_2.id, "alkalinity")
    assert len(values) == 1

    values = params.get_by_type(test_db, user_1.id, "ph")
    assert len(values) == 1

    values = params.get_by_type(test_db, user_1.id, "alkalinity")
    assert len(values) == 0

    delete_from_db(test_db, user_1)
    delete_from_db(test_db, user_2)


def test_can_save_param_with_test_kit(test_db):
    user = save_random_user(test_db)
    aquarium = save_random_aquarium(test_db, user.id)

    value = 9.0

    param = params.create(
        test_db,
        user.id,
        aquarium.id,
        ParamTypes.ALKALINITY,
        value,
    )

    last_value = params.get_by_type(test_db, user.id, ParamTypes.ALKALINITY, limit=1)

    assert len(last_value) == 1
    assert last_value[0].test_kit_name == TestKits.GENERIC_ALKALINITY_DHK.value
    assert last_value[0].value == value

    delete_from_db(test_db, user)


def test_can_save_param_with_convert(test_db):
    user = save_random_user(test_db)
    aquarium = save_random_aquarium(test_db, user.id)

    # string for definition to mimic API call
    param = params.create(
        test_db, user.id, aquarium.id, "alkalinity", 0.5, test_kit="salifert_alkalinity"
    )

    last_value = params.get_by_type(test_db, user.id, ParamTypes.ALKALINITY, limit=1)

    assert len(last_value) == 1
    assert last_value[0].test_kit_name == TestKits.SALIFERT_ALKALINITY.value

    value = math.ceil(last_value[0].value * 10) / 10
    assert value == 7.7

    delete_from_db(test_db, user)
