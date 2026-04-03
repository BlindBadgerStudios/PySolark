import pytest

from pysolark.client import SolArkClient
from pysolark.exceptions import SolArkAPIError

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
    "data": {"id": 10101, "nickname": "user@example.com", "createAt": "2024-08-30T09:14:01Z"},
    "success": True,
}

PLANT_JSON = {
    "code": 0,
    "msg": "Success",
    "data": {
        "id": 424242,
        "name": "Example Plant",
        "currency": {"id": 251, "code": "USD", "text": "$"},
        "timezone": {"id": 327, "code": "America/Los_Angeles", "text": "Pacific"},
        "charges": [],
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

FLOW_JSON = {
    "code": 0,
    "msg": "Success",
    "data": {
        "pvPower": 9974,
        "battPower": 64,
        "gridOrMeterPower": 7905,
        "loadOrEpsPower": 1653,
        "soc": 100.0,
        "toGrid": True,
        "toLoad": True,
        "toBat": True,
    },
    "success": True,
}

USE_JSON = {
    "code": 0,
    "msg": "Success",
    "data": {"load": 5.9, "pv": 13.8, "batteryCharge": 0.2, "gridSell": 7.7},
    "success": True,
}

ERROR_JSON = {"code": 2, "msg": "No Permissions", "success": False}
CSV_TEXT = "Station Name,Load(kWh)\nExample Plant,250.30\n"


class FakeResponse:
    def __init__(self, *, json_data=None, text="", status_code=200, headers=None):
        self._json = json_data
        self.text = text
        self.status_code = status_code
        self.headers = headers or {}

    def json(self):
        if self._json is None:
            raise AssertionError("json() requested for text response")
        return self._json

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class FakeSession:
    def __init__(self):
        self.calls = []

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        if url.endswith("/oauth/token"):
            return FakeResponse(json_data=TOKEN_JSON)
        if url.endswith("/api/v1/user"):
            return FakeResponse(json_data=USER_JSON)
        if url.endswith("/api/v1/plant/424242"):
            return FakeResponse(json_data=PLANT_JSON)
        if url.endswith("/api/v1/plant/424242/realtime"):
            return FakeResponse(json_data=REALTIME_JSON)
        if url.endswith("/api/v1/plant/424242/power/day"):
            return FakeResponse(json_data=POWER_DAY_JSON)
        if url.endswith("/api/v1/plant/energy/424242/month"):
            return FakeResponse(json_data=ENERGY_MONTH_JSON)
        if url.endswith("/api/v1/plant/energy/424242/flow"):
            return FakeResponse(json_data=FLOW_JSON)
        if url.endswith("/api/v1/plant/energy/424242/generation/use"):
            return FakeResponse(json_data=USE_JSON)
        if url.endswith("/api/v1/plant/energy/aggregate"):
            return FakeResponse(text=CSV_TEXT, headers={"content-type": "text/plain; charset=UTF-8"})
        if url.endswith("/api/v1/inverter"):
            return FakeResponse(json_data=ERROR_JSON)
        raise AssertionError(f"Unexpected request: {method} {url}")



def test_client_login_and_validated_queries():
    session = FakeSession()
    client = SolArkClient(username="user@example.com", password="secret", session=session)

    token = client.login()
    assert token.access_token == "access-123"

    user = client.get_current_user()
    assert user.user_id == 10101

    plant = client.get_plant(424242)
    assert plant.name == "Example Plant"

    realtime = client.get_plant_realtime(424242)
    assert realtime.pac == 8701

    power = client.get_plant_power(424242, period="day", date="2026-04-03")
    assert power.records[1].value == 10.5

    energy = client.get_plant_energy(424242, period="month", date="2026-04")
    assert energy.series[0].label == "Load"

    flow = client.get_plant_energy_flow(424242)
    assert flow.to_grid is True

    usage = client.get_plant_generation_use(424242)
    assert usage.pv == 13.8

    report = client.download_plant_energy_aggregate([424242], start_date="2026-04-01", end_date="2026-04-03")
    assert "Example Plant" in report

    login_call = session.calls[0]
    assert login_call[0] == "POST"
    assert login_call[1].endswith("/oauth/token")
    assert login_call[2]["json"] == {
        "grant_type": "password",
        "username": "user@example.com",
        "password": "secret",
    }

    realtime_call = [call for call in session.calls if call[1].endswith("/api/v1/plant/424242/realtime")][0]
    assert realtime_call[2]["headers"]["Authorization"] == "Bearer access-123"

    power_call = [call for call in session.calls if call[1].endswith("/power/day")][0]
    assert power_call[2]["params"] == {"date": "2026-04-03"}


def test_raw_get_allows_exploration_of_undocumented_endpoints():
    session = FakeSession()
    client = SolArkClient(username="user@example.com", password="secret", session=session)
    client.login()

    with pytest.raises(SolArkAPIError):
        client.raw_get("/api/v1/inverter")
