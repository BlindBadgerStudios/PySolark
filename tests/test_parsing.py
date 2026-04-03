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

TOKEN_JSON = {
    "code": 0,
    "msg": "Success",
    "data": {
        "access_token": "access-123",
        "refresh_token": "refresh-456",
        "expires_in": 7200,
        "scope": "all",
        "token_type": "Bearer",
    },
    "success": True,
}

USER_JSON = {
    "code": 0,
    "msg": "Success",
    "data": {
        "id": 10101,
        "nickname": "user@example.com",
        "avatar": "https://mysolark.s3.us-west-2.amazonaws.com/avatar/user1.png",
        "gender": 0,
        "mobile": "555-0100",
        "createAt": "2024-08-30T09:14:01Z",
        "type": None,
        "tempUnit": "℉",
        "company": None,
        "userSrc": "elinter",
        "companyName": None,
        "companyRole": None,
    },
    "success": True,
}

PLANT_JSON = {
    "code": 0,
    "msg": "Success",
    "data": {
        "id": 424242,
        "name": "Example Plant",
        "totalPower": 21.90,
        "thumbUrl": "https://mysolark.s3.us-west-2.amazonaws.com/plant/example.png",
        "joinDate": "2024-08-28T00:00:00Z",
        "type": 2,
        "status": 1,
        "charges": [
            {
                "id": 56145,
                "startRange": "00:00",
                "endRange": "23:59",
                "price": 0.15,
                "type": 1,
                "stationId": 424242,
                "createAt": "2025-02-05T13:45:09Z",
            }
        ],
        "products": None,
        "lon": -122.4194,
        "lat": 37.7749,
        "address": "123 Example Ave",
        "master": {
            "id": 125645,
            "nickname": "installer@example.com",
            "mobile": None,
        },
        "currency": {"id": 251, "code": "USD", "text": "$"},
        "timezone": {
            "id": 327,
            "code": "America/Los_Angeles",
            "text": "(UTC-08:00)Pacific Time (US & Canada)",
        },
        "realtime": {
            "pac": 8701,
            "etoday": 13.7,
            "emonth": 75.1,
            "eyear": 4064.5,
            "etotal": 42781.9,
            "income": 2.1,
            "efficiency": 39.7,
            "updateAt": "2026-04-03T16:37:01Z",
            "currency": {"id": 251, "code": "USD", "text": "$"},
            "totalPower": 21.90,
        },
    },
    "success": True,
}

REALTIME_JSON = {
    "code": 0,
    "msg": "Success",
    "data": {
        "pac": 8701,
        "etoday": 13.7,
        "emonth": 75.1,
        "eyear": 4064.5,
        "etotal": 42781.9,
        "income": 2.1,
        "efficiency": 39.7,
        "updateAt": "2026-04-03T16:37:01Z",
        "currency": {"id": 251, "code": "USD", "text": "$"},
        "totalPower": 21.90,
    },
    "success": True,
}

PLANT_POWER_JSON = {
    "code": 0,
    "msg": "Success",
    "data": {
        "unit": "kWh",
        "records": [
            {"time": "2026-04-01", "value": "32.2", "updateTime": None},
            {"time": "2026-04-02", "value": "29.2", "updateTime": None},
        ],
        "predictedAvg": None,
    },
    "success": True,
}

ENERGY_DAY_JSON = {
    "code": 0,
    "msg": "Success",
    "data": {
        "infos": [
            {
                "unit": "kWh",
                "label": "Load",
                "records": [
                    {"time": "2026-04-01", "value": "71.1", "updateTime": None},
                    {"time": "2026-04-02", "value": "81.6", "updateTime": None},
                ],
            },
            {
                "unit": "kWh",
                "label": "PV",
                "records": [
                    {"time": "2026-04-01", "value": "32.1", "updateTime": None},
                    {"time": "2026-04-02", "value": "29.1", "updateTime": None},
                ],
            },
        ]
    },
    "success": True,
}

ENERGY_FLOW_JSON = {
    "code": 0,
    "msg": "Success",
    "data": {
        "custCode": 29,
        "meterCode": 0,
        "pvPower": 9974,
        "battPower": 64,
        "gridOrMeterPower": 7905,
        "loadOrEpsPower": 1653,
        "genPower": 0,
        "minPower": 0,
        "soc": 100.0,
        "pvTo": True,
        "toLoad": True,
        "toGrid": True,
        "toBat": True,
        "batTo": False,
        "gridTo": False,
        "genTo": False,
        "minTo": False,
        "existsGen": False,
        "existsMin": False,
        "genOn": False,
        "microOn": False,
        "existsMeter": False,
        "bmsCommFaultFlag": False,
        "pv": None,
        "existThinkPower": False,
    },
    "success": True,
}

GENERATION_USE_JSON = {
    "code": 0,
    "msg": "Success",
    "data": {
        "load": 5.9,
        "pv": 13.8,
        "batteryCharge": 0.2,
        "gridSell": 7.7,
    },
    "success": True,
}

CONTACTS_JSON = {
    "code": 0,
    "msg": "Success",
    "data": {"id": 424242, "name": None, "updateAt": "2026-04-03T16:51:16.646+00:00"},
    "success": True,
}

PLANTS_MAP_JSON = {
    "code": 0,
    "msg": "Success",
    "data": [{"id": 424242, "lon": -122.4194, "lat": 37.7749, "status": 1}],
    "success": True,
}

VERSION_JSON = {
    "code": 0,
    "msg": "Success",
    "data": {"version": ""},
    "success": True,
}

COUNT_JSON = {
    "code": 0,
    "msg": "Success",
    "data": {"warning": 0, "fault": 0, "updateAt": "2026-04-03T16:39:49Z", "total": 0, "normal": 0, "offline": 0},
    "success": True,
}

ERROR_JSON = {"code": 2, "msg": "No Permissions", "success": False}


def test_parse_token_user_plant_and_realtime():
    token = parse_token_response(TOKEN_JSON)
    assert token.access_token == "access-123"
    assert token.token_type == "Bearer"

    user = parse_user_response(USER_JSON)
    assert user.user_id == 10101
    assert user.created_at == datetime.fromisoformat("2024-08-30T09:14:01+00:00")

    plant = parse_plant_response(PLANT_JSON)
    assert plant.plant_id == 424242
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

    flow = parse_energy_flow_response(ENERGY_FLOW_JSON)
    assert flow.pv_power == 9974
    assert flow.soc == 100.0
    assert flow.to_grid is True

    usage = parse_generation_use_response(GENERATION_USE_JSON)
    assert usage.load == 5.9
    assert usage.grid_sell == 7.7

    contacts = parse_plant_contacts_response(CONTACTS_JSON)
    assert contacts.plant_id == 424242

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
