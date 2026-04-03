"""Shared test fixtures for PySolark tests."""
from __future__ import annotations

TEST_USER_ID = 10101
TEST_PLANT_ID = 424242
TEST_USERNAME = "operator@example.com"
TEST_PASSWORD = "secret"
TEST_PLANT_NAME = "Example Plant"

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
        "id": TEST_USER_ID,
        "nickname": TEST_USERNAME,
        "avatar": "https://example.invalid/avatar.png",
        "gender": 0,
        "mobile": "555-0100",
        "createAt": "2024-08-30T09:14:01Z",
        "type": None,
        "tempUnit": "℉",
        "company": None,
        "userSrc": "example-source",
        "companyName": None,
        "companyRole": None,
    },
    "success": True,
}

PLANT_JSON = {
    "code": 0,
    "msg": "Success",
    "data": {
        "id": TEST_PLANT_ID,
        "name": TEST_PLANT_NAME,
        "totalPower": 21.90,
        "thumbUrl": "https://example.invalid/plant.png",
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
                "stationId": TEST_PLANT_ID,
                "createAt": "2025-02-05T13:45:09Z",
            }
        ],
        "products": None,
        "lon": -122.4194,
        "lat": 37.7749,
        "address": "123 Example Ave",
        "master": {
            "id": 125645,
            "nickname": "installer@vendor.example",
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

POWER_DAY_JSON = {
    "code": 0,
    "msg": "Success",
    "data": {
        "unit": "W",
        "records": [
            {"time": "00:00", "value": "0.0", "updateTime": None},
            {"time": "00:05", "value": "10.5", "updateTime": None},
        ],
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

ENERGY_MONTH_JSON = {
    "code": 0,
    "msg": "Success",
    "data": {
        "infos": [
            {"label": "Load", "unit": "kWh", "records": [{"time": "2026-04-01", "value": "71.1", "updateTime": None}]},
            {"label": "PV", "unit": "kWh", "records": [{"time": "2026-04-01", "value": "32.1", "updateTime": None}]},
        ]
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

FLOW_JSON = {
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

USE_JSON = {
    "code": 0,
    "msg": "Success",
    "data": {"load": 5.9, "pv": 13.8, "batteryCharge": 0.2, "gridSell": 7.7},
    "success": True,
}

CONTACTS_JSON = {
    "code": 0,
    "msg": "Success",
    "data": {
        "id": TEST_PLANT_ID,
        "name": None,
        "updateAt": "2026-04-03T16:51:16.646+00:00",
    },
    "success": True,
}

PLANTS_MAP_JSON = {
    "code": 0,
    "msg": "Success",
    "data": [{"id": TEST_PLANT_ID, "lon": -122.4194, "lat": 37.7749, "status": 1}],
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

CSV_TEXT = f"Station Name,Load(kWh)\n{TEST_PLANT_NAME},250.30\n"
