from datetime import datetime

import pytest

from pysolark.exceptions import SolArkAPIError
from pysolark.parsing import (
    parse_device_count_response,
    parse_energy_flow_response,
    parse_generation_use_response,
    parse_plant_contacts_response,
    parse_plant_power_response,
    parse_plant_response,
    parse_plants_map_response,
    parse_realtime_response,
    parse_token_response,
    parse_user_response,
    parse_version_response,
)

from .fixtures import (
    CONTACTS_JSON,
    COUNT_JSON,
    ENERGY_DAY_JSON,
    ERROR_JSON,
    FLOW_JSON,
    PLANT_JSON,
    PLANT_POWER_JSON,
    PLANTS_MAP_JSON,
    REALTIME_JSON,
    TOKEN_JSON,
    USE_JSON,
    USER_JSON,
    VERSION_JSON,
    TEST_PLANT_ID,
    TEST_USER_ID,
)


def test_parse_token_user_plant_and_realtime():
    token = parse_token_response(TOKEN_JSON)
    assert token.access_token == "access-123"
    assert token.token_type == "Bearer"

    user = parse_user_response(USER_JSON)
    assert user.user_id == TEST_USER_ID
    assert user.created_at == datetime.fromisoformat("2024-08-30T09:14:01+00:00")

    plant = parse_plant_response(PLANT_JSON)
    assert plant.plant_id == TEST_PLANT_ID
    assert plant.currency.code == "USD"
    assert plant.realtime.pac == 8701
    assert plant.charges[0].price == 0.15

    realtime = parse_realtime_response(REALTIME_JSON)
    assert realtime.etoday == 13.7
    assert realtime.updated_at == datetime.fromisoformat("2026-04-03T16:37:01+00:00")


def test_parse_power_energy_flow_and_generation_use():
    power = parse_plant_power_response(PLANT_POWER_JSON)
    assert power.unit == "kWh"
    assert power.records[1].value == 29.2

    energy = parse_plant_power_response(ENERGY_DAY_JSON, collection_key="infos")
    assert len(energy.series) == 2
    assert energy.series[0].label == "Load"
    assert energy.series[1].records[0].value == 32.1

    flow = parse_energy_flow_response(FLOW_JSON)
    assert flow.pv_power == 9974
    assert flow.soc == 100.0
    assert flow.to_grid is True

    usage = parse_generation_use_response(USE_JSON)
    assert usage.load == 5.9
    assert usage.grid_sell == 7.7

    contacts = parse_plant_contacts_response(CONTACTS_JSON)
    assert contacts.plant_id == TEST_PLANT_ID

    plants_map = parse_plants_map_response(PLANTS_MAP_JSON)
    assert plants_map[0].latitude == 37.7749

    version = parse_version_response(VERSION_JSON)
    assert version.version == ""

    count = parse_device_count_response(COUNT_JSON)
    assert count.total == 0
    assert count.updated_at == datetime.fromisoformat("2026-04-03T16:39:49+00:00")


def test_nonzero_code_raises_api_error():
    with pytest.raises(SolArkAPIError) as exc:
        parse_realtime_response(ERROR_JSON)

    assert exc.value.code == 2
    assert str(exc.value) == "Sol-Ark API error 2: No Permissions"


def test_parse_datetime_tolerates_bad_values():
    from pysolark.parsing import _parse_datetime

    assert _parse_datetime(None) is None
    assert _parse_datetime("") is None
    assert _parse_datetime("not-a-date") is None


def test_parse_float_tolerates_bad_values():
    from pysolark.parsing import _parse_float

    assert _parse_float(None) is None
    assert _parse_float("") is None
    assert _parse_float("null") is None
    assert _parse_float({"unexpected": "dict"}) is None
    assert _parse_float([1, 2]) is None
    assert _parse_float("42.5") == 42.5
