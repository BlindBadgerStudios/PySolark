import pytest

from pysolark.client import SolArkClient
from pysolark.exceptions import SolArkAPIError

from .fixtures import (
    CONTACTS_JSON,
    COUNT_JSON,
    ENERGY_MONTH_JSON,
    ERROR_JSON,
    FLOW_JSON,
    PLANT_JSON,
    PLANTS_MAP_JSON,
    POWER_DAY_JSON,
    REALTIME_JSON,
    TOKEN_JSON,
    USE_JSON,
    USER_JSON,
    VERSION_JSON,
    CSV_TEXT,
    TEST_PLANT_ID,
    TEST_PLANT_NAME,
    TEST_USERNAME,
    TEST_PASSWORD,
    TEST_USER_ID,
)


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

    def close(self):
        pass

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        if url.endswith("/oauth/token"):
            return FakeResponse(json_data=TOKEN_JSON)
        if url.endswith("/api/v1/user"):
            return FakeResponse(json_data=USER_JSON)
        if url.endswith(f"/api/v1/plant/{TEST_PLANT_ID}"):
            return FakeResponse(json_data=PLANT_JSON)
        if url.endswith(f"/api/v1/plant/{TEST_PLANT_ID}/realtime"):
            return FakeResponse(json_data=REALTIME_JSON)
        if url.endswith(f"/api/v1/plant/{TEST_PLANT_ID}/power/day"):
            return FakeResponse(json_data=POWER_DAY_JSON)
        if url.endswith(f"/api/v1/plant/energy/{TEST_PLANT_ID}/month"):
            return FakeResponse(json_data=ENERGY_MONTH_JSON)
        if url.endswith(f"/api/v1/plant/energy/{TEST_PLANT_ID}/flow"):
            return FakeResponse(json_data=FLOW_JSON)
        if url.endswith(f"/api/v1/plant/energy/{TEST_PLANT_ID}/generation/use"):
            return FakeResponse(json_data=USE_JSON)
        if url.endswith("/api/v1/plant/energy/aggregate"):
            return FakeResponse(text=CSV_TEXT, headers={"content-type": "text/plain; charset=UTF-8"})
        if url.endswith(f"/api/v1/plant/{TEST_PLANT_ID}/contacts"):
            return FakeResponse(json_data=CONTACTS_JSON)
        if url.endswith("/api/v1/plants/map"):
            return FakeResponse(json_data=PLANTS_MAP_JSON)
        if url.endswith("/api/v1/version/latest"):
            return FakeResponse(json_data=VERSION_JSON)
        if url.endswith("/api/v1/batteries/count"):
            return FakeResponse(json_data=COUNT_JSON)
        if url.endswith("/api/v1/inverters/count"):
            return FakeResponse(json_data=COUNT_JSON)
        if url.endswith("/api/v1/inverter"):
            return FakeResponse(json_data=ERROR_JSON)
        raise AssertionError(f"Unexpected request: {method} {url}")


def test_client_login_and_validated_queries():
    session = FakeSession()
    client = SolArkClient(username=TEST_USERNAME, password=TEST_PASSWORD, session=session)

    token = client.login()
    assert token.access_token == "access-123"

    user = client.get_current_user()
    assert user.user_id == TEST_USER_ID

    plant = client.get_plant(TEST_PLANT_ID)
    assert plant.name == TEST_PLANT_NAME

    realtime = client.get_plant_realtime(TEST_PLANT_ID)
    assert realtime.pac == 8701

    power = client.get_plant_power(TEST_PLANT_ID, period="day", date="2026-04-03")
    assert power.records[1].value == 10.5

    energy = client.get_plant_energy(TEST_PLANT_ID, period="month", date="2026-04")
    assert energy.series[0].label == "Load"

    flow = client.get_plant_energy_flow(TEST_PLANT_ID)
    assert flow.to_grid is True

    usage = client.get_plant_generation_use(TEST_PLANT_ID)
    assert usage.pv == 13.8

    report = client.download_plant_energy_aggregate([TEST_PLANT_ID], start_date="2026-04-01", end_date="2026-04-03")
    assert TEST_PLANT_NAME in report

    contacts = client.get_plant_contacts(TEST_PLANT_ID)
    assert contacts.plant_id == TEST_PLANT_ID

    plants_map = client.get_plants_map()
    assert plants_map[0].plant_id == TEST_PLANT_ID

    latest_version = client.get_latest_version()
    assert latest_version.version == ""

    battery_count = client.get_batteries_count()
    inverter_count = client.get_inverters_count()
    assert battery_count.total == 0
    assert inverter_count.updated_at is not None

    login_call = session.calls[0]
    assert login_call[0] == "POST"
    assert login_call[1].endswith("/oauth/token")
    assert login_call[2]["json"] == {
        "grant_type": "password",
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD,
    }

    realtime_call = [c for c in session.calls if c[1].endswith(f"/api/v1/plant/{TEST_PLANT_ID}/realtime")][0]
    assert realtime_call[2]["headers"]["Authorization"] == "Bearer access-123"

    power_call = [c for c in session.calls if c[1].endswith("/power/day")][0]
    assert power_call[2]["params"] == {"date": "2026-04-03"}


def test_list_plants_returns_map_points():
    session = FakeSession()
    client = SolArkClient(username=TEST_USERNAME, password=TEST_PASSWORD, session=session)
    client.login()

    plants = client.list_plants()
    assert len(plants) == 1
    assert plants[0].plant_id == TEST_PLANT_ID


def test_context_manager_closes_session():
    closed = []

    class TrackingSession(FakeSession):
        def close(self):
            closed.append(True)

    with SolArkClient(username=TEST_USERNAME, password=TEST_PASSWORD, session=TrackingSession()) as client:
        client.login()
        assert client.token is not None

    assert closed == [True]


def test_raw_get_allows_exploration_of_undocumented_endpoints():
    session = FakeSession()
    client = SolArkClient(username=TEST_USERNAME, password=TEST_PASSWORD, session=session)
    client.login()

    with pytest.raises(SolArkAPIError):
        client.raw_get("/api/v1/inverter")
