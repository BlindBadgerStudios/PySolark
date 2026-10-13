from __future__ import annotations

import logging
import re
import time
from collections.abc import Callable
from datetime import UTC, date, datetime
from typing import Any, Literal, Self

from requests import RequestException, Session

from .exceptions import SolArkAPIError, SolArkAuthError, SolArkTokenExpiredError
from .models import (
    SolArkDeviceCount,
    SolArkEnergyFlow,
    SolArkGenerationUse,
    SolArkPlant,
    SolArkPlantContacts,
    SolArkPlantMapPoint,
    SolArkRealtime,
    SolArkSeriesCollection,
    SolArkToken,
    SolArkUser,
    SolArkVersionInfo,
)
from .parsing import (
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

logger = logging.getLogger(__name__)


def _default_date(period: str) -> str:
    today = date.today()
    if period == "day":
        return today.isoformat()  # "2026-06-17"
    if period == "month":
        return today.strftime("%Y-%m")  # "2026-06"
    return str(today.year)  # "2026" for year/total


RETRYABLE_STATUS = frozenset({429, 502, 503, 504})


# Sol-Ark does not document its envelope error codes. These are heuristics for auth failures
# that come back as HTTP 200 with a non-zero ``code``.
AUTH_ERROR_CODES = frozenset({401, 403})
_AUTH_MESSAGE_RE = re.compile(
    r"token|unauthori[sz]ed|not logged in|login (?:expired|required)|re-?login", re.IGNORECASE
)


def is_auth_envelope(code: Any, message: Any) -> bool:
    """Return True when an envelope error looks like an authentication failure."""
    try:
        if int(code) in AUTH_ERROR_CODES:
            return True
    except (TypeError, ValueError):
        pass
    return bool(message) and bool(_AUTH_MESSAGE_RE.search(str(message)))


def _check_envelope(payload: Any) -> dict[str, Any]:
    """Raise SolArkAPIError (or SolArkAuthError) for non-dict payloads or a non-zero envelope ``code``."""
    if not isinstance(payload, dict):
        raise SolArkAPIError(-1, f"Unexpected response payload type: {type(payload).__name__}")
    code = payload.get("code", 0)
    if code != 0:
        message = payload.get("msg", "Unknown error")
        if is_auth_envelope(code, message):
            raise SolArkAuthError(code, message, payload)
        raise SolArkAPIError(code, message, payload)
    return payload


class SolArkClient:
    api_root = "https://api.solarkcloud.com"

    def __init__(
        self,
        username: str,
        password: str,
        *,
        session: Session | None = None,
        timeout: int = 30,
        max_retries: int = 3,
        backoff_factor: float = 1.0,
        max_backoff: float = 60.0,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self.username = username
        self._password = password
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.max_backoff = max_backoff
        self._sleep = sleep
        self.session = session or Session()
        self.token: SolArkToken | None = None

    def __repr__(self) -> str:
        authenticated = self.token is not None
        return f"{type(self).__name__}(username={self.username!r}, password='***', authenticated={authenticated})"

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: object) -> None:
        self.session.close()

    def _headers(self) -> dict[str, str]:
        if not self.token:
            raise ValueError("Not authenticated. Call login() first.")
        if self.token.expires_at and datetime.now(UTC) >= self.token.expires_at:
            raise SolArkTokenExpiredError()
        return {"Authorization": f"Bearer {self.token.access_token}", "Accept": "application/json"}

    def _retry_delay(self, attempt: int, response: Any = None) -> float:
        if response is not None:
            retry_after = (getattr(response, "headers", None) or {}).get("Retry-After")
            if retry_after is not None:
                try:
                    return min(max(float(retry_after), 0.0), self.max_backoff)
                except ValueError:
                    pass
        return min(self.backoff_factor * (2**attempt), self.max_backoff)

    def _request(self, method: str, path: str, **kwargs: Any):
        """Send a request. Only idempotent GETs are retried (429/5xx/connection errors).

        POSTs, in particular ``POST /oauth/token``, are never retried: a retried login can
        create extra sessions on the account.
        """
        url = f"{self.api_root}{path}"
        retries = self.max_retries if method.upper() == "GET" else 0
        attempt = 0
        while True:
            logger.debug("%s %s attempt=%d", method, path, attempt + 1)
            try:
                response = self.session.request(method, url, timeout=self.timeout, **kwargs)
            except RequestException:
                if attempt >= retries:
                    raise
                delay = self._retry_delay(attempt)
                logger.warning("%s %s failed with a connection error; retrying in %.1fs", method, path, delay)
            else:
                if response.status_code not in RETRYABLE_STATUS or attempt >= retries:
                    response.raise_for_status()
                    return response
                delay = self._retry_delay(attempt, response)
                logger.warning("%s %s returned HTTP %d; retrying in %.1fs", method, path, response.status_code, delay)
            self._sleep(delay)
            attempt += 1

    def _token_request(self, body: dict[str, Any]) -> SolArkToken:
        # Never retried (see _request): a retried token POST can create extra sessions.
        response = self._request("POST", "/oauth/token", json=body)
        try:
            payload = response.json()
        except ValueError as exc:
            raise SolArkAuthError(-1, "Token endpoint returned a non-JSON response") from exc
        if not isinstance(payload, dict) or payload.get("code", 0) != 0:
            code = payload.get("code", -1) if isinstance(payload, dict) else -1
            message = payload.get("msg", "Unknown error") if isinstance(payload, dict) else "Unexpected payload"
            raise SolArkAuthError(code, message)
        return parse_token_response(payload)

    def login(self) -> SolArkToken:
        """Full password login. Prefer ``renew()`` once a token exists."""
        logger.debug("POST /oauth/token grant_type=password")
        self.token = self._token_request(
            {
                "grant_type": "password",
                "username": self.username,
                "password": self._password,
            }
        )
        logger.debug("login successful expires_in=%s", self.token.expires_in)
        return self.token

    def refresh(self) -> SolArkToken:
        """Exchange the stored refresh token for a new access token.

        Sol-Ark does not document this grant. It follows the standard OAuth2 ``refresh_token``
        grant that third-party Sol-Ark clients use against the same endpoint.
        """
        if self.token is None or not self.token.refresh_token:
            raise SolArkAuthError(-1, "No refresh token available")
        logger.debug("POST /oauth/token grant_type=refresh_token")
        old_refresh = self.token.refresh_token
        token = self._token_request({"grant_type": "refresh_token", "refresh_token": old_refresh})
        if not token.refresh_token:
            token.refresh_token = old_refresh
        self.token = token
        logger.debug("refresh successful expires_in=%s", self.token.expires_in)
        return self.token

    def renew(self) -> SolArkToken:
        """Renew the session: try the refresh token first, then fall back to a password login."""
        if self.token is not None and self.token.refresh_token:
            try:
                return self.refresh()
            except (SolArkAPIError, RequestException) as exc:
                logger.info("Token refresh failed (%s); falling back to password login", type(exc).__name__)
        return self.login()

    def get_current_user(self) -> SolArkUser:
        return parse_user_response(self.raw_get("/api/v1/user"))

    def get_plant(self, plant_id: int) -> SolArkPlant:
        return parse_plant_response(self.raw_get(f"/api/v1/plant/{plant_id}"))

    def get_plant_realtime(self, plant_id: int) -> SolArkRealtime:
        return parse_realtime_response(self.raw_get(f"/api/v1/plant/{plant_id}/realtime"))

    def get_plant_power(
        self, plant_id: int, *, period: Literal["day", "month", "year", "total"], date: str | None = None
    ) -> SolArkSeriesCollection:
        resolved = date or _default_date(period)
        return parse_plant_power_response(
            self.raw_get(f"/api/v1/plant/{plant_id}/power/{period}", params={"date": resolved})
        )

    def get_plant_energy(
        self, plant_id: int, *, period: Literal["day", "month", "year", "total"], date: str | None = None
    ) -> SolArkSeriesCollection:
        resolved = date or _default_date(period)
        return parse_plant_power_response(
            self.raw_get(f"/api/v1/plant/energy/{plant_id}/{period}", params={"date": resolved}),
            collection_key="infos",
        )

    def get_plant_energy_flow(self, plant_id: int) -> SolArkEnergyFlow:
        return parse_energy_flow_response(self.raw_get(f"/api/v1/plant/energy/{plant_id}/flow"))

    def get_plant_generation_use(self, plant_id: int) -> SolArkGenerationUse:
        return parse_generation_use_response(self.raw_get(f"/api/v1/plant/energy/{plant_id}/generation/use"))

    def get_plant_contacts(self, plant_id: int) -> SolArkPlantContacts:
        logger.debug("POST /api/v1/plant/%s/contacts", plant_id)
        response = self._request(
            "POST",
            f"/api/v1/plant/{plant_id}/contacts",
            headers=self._headers(),
            json={"id": plant_id},
        )
        payload = _check_envelope(response.json())
        return parse_plant_contacts_response(payload)

    def list_plants(self) -> list[SolArkPlantMapPoint]:
        return parse_plants_map_response(self.raw_get("/api/v1/plants/map"))

    def get_plants_map(self) -> list[SolArkPlantMapPoint]:
        return parse_plants_map_response(self.raw_get("/api/v1/plants/map"))

    def get_latest_version(self) -> SolArkVersionInfo:
        return parse_version_response(self.raw_get("/api/v1/version/latest"))

    def get_batteries_count(self) -> SolArkDeviceCount:
        return parse_device_count_response(self.raw_get("/api/v1/batteries/count"))

    def get_inverters_count(self) -> SolArkDeviceCount:
        return parse_device_count_response(self.raw_get("/api/v1/inverters/count"))

    def download_plant_energy_aggregate(self, plant_ids: list[int], *, start_date: str, end_date: str) -> str:
        response = self._request(
            "GET",
            "/api/v1/plant/energy/aggregate",
            headers=self._headers(),
            params={
                "plantIds": ",".join(str(plant_id) for plant_id in plant_ids),
                "startDate": start_date,
                "endDate": end_date,
            },
        )
        content_type = response.headers.get("content-type", "")
        if "json" in content_type or response.text.lstrip().startswith("{"):
            # The CSV endpoint reports failures as a JSON envelope, not as CSV text.
            try:
                payload = response.json()
            except ValueError:
                payload = None
            if payload is not None:
                _check_envelope(payload)
                raise SolArkAPIError(-1, "Expected CSV from aggregate download but got JSON", payload)
        return response.text

    def raw_get(self, path: str, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        response = self._request("GET", path, headers=self._headers(), params=params)
        return _check_envelope(response.json())
