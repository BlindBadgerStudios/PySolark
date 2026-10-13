import pytest

from pysolark.client import SolArkClient
from pysolark.exceptions import SolArkAPIError

from .fixtures import (
    CONTACTS_JSON,
    COUNT_JSON,
    CSV_TEXT,
    ENERGY_MONTH_JSON,
    ERROR_JSON,
    FLOW_JSON,
    PLANT_JSON,
    PLANTS_MAP_JSON,
    POWER_DAY_JSON,
    REALTIME_JSON,
    TEST_PASSWORD,
    TEST_PLANT_ID,
    TEST_PLANT_NAME,
    TEST_USER_ID,
    TEST_USERNAME,
    TOKEN_JSON,
    USE_JSON,
    USER_JSON,
    VERSION_JSON,
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

    realtime_call = next(c for c in session.calls if c[1].endswith(f"/api/v1/plant/{TEST_PLANT_ID}/realtime"))
    assert realtime_call[2]["headers"]["Authorization"] == "Bearer access-123"

    power_call = next(c for c in session.calls if c[1].endswith("/power/day"))
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


def test_token_and_client_repr_redact_secrets():
    session = FakeSession()
    client = SolArkClient(username=TEST_USERNAME, password=TEST_PASSWORD, session=session)
    token = client.login()

    assert token.access_token not in repr(token)
    assert token.refresh_token not in repr(token)
    assert "raw=" not in repr(token)
    assert TEST_PASSWORD not in repr(client)
    assert token.access_token not in repr(client)
    assert not hasattr(client, "password")


class _SingleResponseSession(FakeSession):
    def __init__(self, response):
        super().__init__()
        self.response = response

    def request(self, method, url, **kwargs):
        if url.endswith("/oauth/token"):
            return super().request(method, url, **kwargs)
        self.calls.append((method, url, kwargs))
        return self.response


def test_aggregate_download_raises_on_error_envelope():
    session = _SingleResponseSession(
        FakeResponse(json_data=ERROR_JSON, text='{"code": 2}', headers={"content-type": "application/json"})
    )
    client = SolArkClient(username=TEST_USERNAME, password=TEST_PASSWORD, session=session)
    client.login()
    with pytest.raises(SolArkAPIError):
        client.download_plant_energy_aggregate([TEST_PLANT_ID], start_date="2026-04-01", end_date="2026-04-03")


def test_raw_get_rejects_non_dict_payload():
    session = _SingleResponseSession(FakeResponse(json_data=["not", "a", "dict"]))
    client = SolArkClient(username=TEST_USERNAME, password=TEST_PASSWORD, session=session)
    client.login()
    with pytest.raises(SolArkAPIError):
        client.raw_get("/api/v1/user")


class _ScriptedSession(FakeSession):
    """Returns queued responses (or raises queued exceptions) in order."""

    def __init__(self, responses):
        super().__init__()
        self.responses = list(responses)

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        item = self.responses.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


def _client(session, sleeps):
    return SolArkClient(username=TEST_USERNAME, password=TEST_PASSWORD, session=session, sleep=sleeps.append)


def test_login_post_is_never_retried():
    sleeps = []
    session = _ScriptedSession([FakeResponse(status_code=503), FakeResponse(json_data=TOKEN_JSON)])
    client = _client(session, sleeps)
    with pytest.raises(RuntimeError):
        client.login()
    assert len(session.calls) == 1
    assert sleeps == []


def test_get_retries_429_honouring_retry_after():
    sleeps = []
    session = _ScriptedSession(
        [
            FakeResponse(json_data=TOKEN_JSON),
            FakeResponse(status_code=429, headers={"Retry-After": "7"}),
            FakeResponse(status_code=502),
            FakeResponse(json_data=USER_JSON),
        ]
    )
    client = _client(session, sleeps)
    client.login()
    user = client.get_current_user()
    assert user.user_id == TEST_USER_ID
    assert sleeps == [7.0, 2.0]


def test_get_retries_connection_errors_then_gives_up():
    import requests

    sleeps = []
    session = _ScriptedSession(
        [FakeResponse(json_data=TOKEN_JSON)] + [requests.ConnectionError("boom") for _ in range(4)]
    )
    client = _client(session, sleeps)
    client.login()
    with pytest.raises(requests.ConnectionError):
        client.get_current_user()
    assert sleeps == [1.0, 2.0, 4.0]


def test_get_does_not_retry_client_errors():
    sleeps = []
    session = _ScriptedSession([FakeResponse(json_data=TOKEN_JSON), FakeResponse(status_code=404)])
    client = _client(session, sleeps)
    client.login()
    with pytest.raises(RuntimeError):
        client.get_current_user()
    assert sleeps == []


def test_envelope_auth_error_in_http_200_raises_auth_error():
    from pysolark import SolArkAuthError

    sleeps = []
    session = _ScriptedSession(
        [FakeResponse(json_data=TOKEN_JSON), FakeResponse(json_data={"code": 401, "msg": "token invalid"})]
    )
    client = _client(session, sleeps)
    client.login()
    with pytest.raises(SolArkAuthError):
        client.get_current_user()


def test_non_auth_envelope_error_is_plain_api_error():
    from pysolark import SolArkAuthError

    session = _ScriptedSession([FakeResponse(json_data=TOKEN_JSON), FakeResponse(json_data=ERROR_JSON)])
    client = _client(session, [])
    client.login()
    with pytest.raises(SolArkAPIError) as excinfo:
        client.get_current_user()
    assert not isinstance(excinfo.value, SolArkAuthError)


def test_login_envelope_failure_raises_auth_error():
    from pysolark import SolArkAuthError

    session = _ScriptedSession([FakeResponse(json_data={"code": 102, "msg": "Bad credentials"})])
    client = _client(session, [])
    with pytest.raises(SolArkAuthError):
        client.login()
    assert client.token is None


def test_renew_uses_refresh_token_first():
    refreshed = {"code": 0, "data": {"access_token": "access-new", "expires_in": 3600}}
    session = _ScriptedSession([FakeResponse(json_data=TOKEN_JSON), FakeResponse(json_data=refreshed)])
    client = _client(session, [])
    old_refresh = client.login().refresh_token
    token = client.renew()
    assert token.access_token == "access-new"
    assert token.refresh_token == old_refresh
    assert session.calls[1][2]["json"] == {"grant_type": "refresh_token", "refresh_token": old_refresh}
    assert len(session.calls) == 2


def test_renew_falls_back_to_password_login_when_refresh_fails():
    session = _ScriptedSession(
        [
            FakeResponse(json_data=TOKEN_JSON),
            FakeResponse(json_data={"code": 401, "msg": "invalid refresh token"}),
            FakeResponse(json_data=TOKEN_JSON),
        ]
    )
    client = _client(session, [])
    client.login()
    client.renew()
    assert [call[2]["json"]["grant_type"] for call in session.calls] == ["password", "refresh_token", "password"]


def test_renew_without_token_does_password_login():
    session = _ScriptedSession([FakeResponse(json_data=TOKEN_JSON)])
    client = _client(session, [])
    client.renew()
    assert session.calls[0][2]["json"]["grant_type"] == "password"


def test_is_auth_envelope_heuristics():
    from pysolark.client import is_auth_envelope

    assert is_auth_envelope(401, "whatever")
    assert is_auth_envelope(5, "Access token expired")
    assert not is_auth_envelope(2, "No Permissions")
