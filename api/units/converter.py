from api.config import ParamTypes, TestKits


def convert_alkalinity_salifert_alk(value: float):
    # 0.0mL = 15.7
    # 0.98mL = 0.0
    # y = (15.7 / 0.98) x - 15.7
    # y(0.98) = -15.7 / 0.98 * 0.98  + 15.7  = 0
    # y(0.0) = -15.7 / 0.98 * 0 + 15.7 = 0
    # y(0.5) = -15.7 / 0.98 * 0.5 + 15.7 = 7.689795918367347
    return -15.7 / 0.98 * value + 15.7


def convert_hanna_phosphorus_ulr(value: float):
    return value


def no_convert(value: float):
    return value


converters = {
    ParamTypes.PH: {
        TestKits.GENERIC_PH: no_convert,
    },
    ParamTypes.ALKALINITY: {
        TestKits.GENERIC_ALKALINITY_DHK: no_convert,
        TestKits.SALIFERT_ALKALINITY: convert_alkalinity_salifert_alk,
    },
    ParamTypes.PHOSPHATE: {
        TestKits.GENERIC_PHOSPHATE_PPM: no_convert,
        TestKits.HANNA_PHOSPHORUS_ULR: convert_hanna_phosphorus_ulr,
    },
    ParamTypes.CALCIUM: {
        TestKits.GENERIC_CALCIUM_PPM: no_convert,
    },
    ParamTypes.MAGNESIUM: {
        TestKits.GENERIC_MAGNESIUM_PPM: no_convert,
    },
    ParamTypes.NITRATE: {
        TestKits.GENERIC_NITRATE_PPM: no_convert,
    },
}


def convert_unit_for(
    param_type: ParamTypes, test_kit: TestKits, value: float
) -> float | None:
    """Convert to 'param_type' db units"""
    if param_type in converters and test_kit in converters[param_type]:
        return converters[param_type][test_kit](value)
    else:
        return None
