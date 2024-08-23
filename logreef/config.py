import os
from enum import Enum


class ParamTypes(Enum):
    PH = "ph"
    ALKALINITY = "alkalinity"
    PHOSPHATE = "phosphate"
    CALCIUM = "calcium"
    MAGNESIUM = "magnesium"
    NITRATE = "nitrate"


# string needs to correspond to db 'test_kits' name primary key
class TestKits(Enum):
    GENERIC_ALKALINITY_DHK = "generic_dkh"
    GENERIC_CALCIUM_PPM = "generic_calcium_ppm"
    GENERIC_MAGNESIUM_PPM = "generic_magnesium_ppm"
    GENERIC_PHOSPHATE_PPM = "generic_phosphate_ppm"
    GENERIC_NITRATE_PPM = "generic_nitrate_ppm"
    GENERIC_PH = "generic_ph"
    SALIFERT_ALKALINITY = "salifert_alkalinity"
    HANNA_PHOSPHORUS_ULR = "hanna_phosphorus_ulr"
    HANNA_NITRATE = "hanna_nitrate"


class ConfigAPI(Enum):
    SECRET_KEY = "secret_key"
    ALGORITHM = "algorithm"
    DB_URL = "db_url"
    ACCESS_TOKEN_EXPIRE_MINUTES = "access_token_expire_minutes"
    TEST_USERNAME = "test_username"
    TEST_PASSWORD = "test_password"
    TEST_AQUARIUM_NAME = "test_aquarium_name"


default_test_kits = {
    "alkalinity": TestKits.GENERIC_ALKALINITY_DHK,
    "phosphate": TestKits.GENERIC_PHOSPHATE_PPM,
    "calcium": TestKits.GENERIC_CALCIUM_PPM,
    "magnesium": TestKits.GENERIC_MAGNESIUM_PPM,
    "nitrate": TestKits.GENERIC_NITRATE_PPM,
    "ph": TestKits.GENERIC_PH,
}

api_configs = {
    ConfigAPI.SECRET_KEY: "N5fkubrSj2eV7bXZ4JNMoZEvN2WFZIS56TfRLEx6TxA",  # openssl rand -base64 32, production overriden thu env. variables
    ConfigAPI.ALGORITHM: "HS256",
    ConfigAPI.DB_URL: "sqlite:///./logreef/logreef.db",
    ConfigAPI.ACCESS_TOKEN_EXPIRE_MINUTES: 24 * 60,
    ConfigAPI.TEST_USERNAME: "test",
    ConfigAPI.TEST_PASSWORD: "test",
    ConfigAPI.TEST_AQUARIUM_NAME: "test",
}


def get_param_type(param_type_name: str) -> ParamTypes:
    param_type_names = [
        param_type.name
        for param_type in ParamTypes
        if param_type.value == param_type_name
    ]
    if len(param_type_names) != 1:
        raise Exception(f"{param_type_name} not supported")
    return ParamTypes[param_type_names[0]]


def get_test_kit(test_kit_name: str) -> TestKits:
    test_kit_names = [
        test_kit.name for test_kit in TestKits if test_kit.value == test_kit_name
    ]
    if len(test_kit_names) != 1:
        raise Exception(f"{test_kit_name} not supported")
    return TestKits[test_kit_names[0]]


def get_config(config: ConfigAPI):
    # check if available in env variables
    name = config.value
    if name in os.environ:
        return os.environ[name]
    else:
        return api_configs[config]
