from __future__ import annotations

import logging
from typing import Any, Literal

from requests import Session

logger = logging.getLogger(__name__)

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


class SolArkClient:
    api_root = "https://api.solarkcloud.com"

    def __init__(
        self,
        username: str,
        password: str,
        *,
        session: Session | None = None,
        timeout: int = 30,
    ) -> None:
        self.username = username
        self.password = password
        self.timeout = timeout
        self.session = session or Session()
        self.token: SolArkToken | None = None

    def __enter__(self) -> SolArkClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.session.close()

    def _headers(self) -> dict[str, str]:
        if not self.token:
            raise ValueError("Not authenticated. Call login() first.")
        return {"Authorization": f"Bearer {self.token.access_token}", "Accept": "application/json"}

    def _request(self, method: str, path: str, **kwargs: Any):
        logger.debug("%s %s", method, path)
        response = self.session.request(method, f"{self.api_root}{path}", timeout=self.timeout, **kwargs)
        response.raise_for_status()
        return response

    def login(self) -> SolArkToken:
        logger.debug("POST /oauth/token user=%s", self.username)
        response = self._request(
            "POST",
            "/oauth/token",
            json={
                "grant_type": "password",
                "username": self.username,
                "password": self.password,
            },
        )
        self.token = parse_token_response(response.json())
        logger.debug("login successful expires_in=%s", self.token.expires_in)
        return self.token

    def get_current_user(self) -> SolArkUser:
        return parse_user_response(self.raw_get("/api/v1/user"))

    def get_plant(self, plant_id: int) -> SolArkPlant:
        return parse_plant_response(self.raw_get(f"/api/v1/plant/{plant_id}"))

    def get_plant_realtime(self, plant_id: int) -> SolArkRealtime:
        return parse_realtime_response(self.raw_get(f"/api/v1/plant/{plant_id}/realtime"))

    def get_plant_power(self, plant_id: int, *, period: Literal["day", "month", "year", "total"], date: str | None = None) -> SolArkSeriesCollection:
        params = {"date": date} if date is not None else None
        return parse_plant_power_response(self.raw_get(f"/api/v1/plant/{plant_id}/power/{period}", params=params))

    def get_plant_energy(self, plant_id: int, *, period: Literal["day", "month", "year", "total"], date: str | None = None) -> SolArkSeriesCollection:
        params = {"date": date} if date is not None else None
        return parse_plant_power_response(
            self.raw_get(f"/api/v1/plant/energy/{plant_id}/{period}", params=params),
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
        payload = response.json()
        code = payload.get("code", 0)
        if code != 0:
            from .exceptions import SolArkAPIError
            raise SolArkAPIError(code, payload.get("msg", "Unknown error"), payload)
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
        return response.text

    def raw_get(self, path: str, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        response = self._request("GET", path, headers=self._headers(), params=params)
        payload = response.json()
        code = payload.get("code", 0)
        if code != 0:
            from .exceptions import SolArkAPIError
            raise SolArkAPIError(code, payload.get("msg", "Unknown error"), payload)
        return payload
