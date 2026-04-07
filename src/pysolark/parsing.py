from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from .exceptions import SolArkAPIError
from .models import (
    SolArkChargeWindow,
    SolArkCurrency,
    SolArkDeviceCount,
    SolArkEnergyFlow,
    SolArkGenerationUse,
    SolArkPlant,
    SolArkPlantContacts,
    SolArkPlantMapPoint,
    SolArkPoint,
    SolArkRealtime,
    SolArkSeries,
    SolArkSeriesCollection,
    SolArkTimezone,
    SolArkToken,
    SolArkUser,
    SolArkVersionInfo,
)

logger = logging.getLogger(__name__)


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        logger.warning("Could not parse datetime value: %r", value)
        return None


def _parse_float(value: Any) -> float | None:
    if value in (None, "", "null"):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        logger.warning("Could not parse float value: %r", value)
        return None



def _unwrap(payload: dict[str, Any]) -> dict[str, Any]:
    code = payload.get("code", 0)
    if code != 0:
        raise SolArkAPIError(code, payload.get("msg", "Unknown error"), payload)
    data = payload.get("data")
    return data if isinstance(data, dict) else {"items": data}



def _parse_currency(payload: dict[str, Any] | None) -> SolArkCurrency | None:
    if not payload:
        return None
    return SolArkCurrency(
        currency_id=payload.get("id"),
        code=payload.get("code"),
        text=payload.get("text"),
        raw=payload,
    )



def _parse_timezone(payload: dict[str, Any] | None) -> SolArkTimezone | None:
    if not payload:
        return None
    return SolArkTimezone(
        timezone_id=payload.get("id"),
        code=payload.get("code"),
        text=payload.get("text"),
        raw=payload,
    )



def _parse_point(payload: dict[str, Any]) -> SolArkPoint:
    return SolArkPoint(
        time=payload.get("time", ""),
        value=_parse_float(payload.get("value")),
        updated_at=_parse_datetime(payload.get("updateTime")),
    )



def parse_token_response(payload: dict[str, Any]) -> SolArkToken:
    data = _unwrap(payload)
    expires_in = data.get("expires_in")
    expires_at = (
        datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        if expires_in is not None
        else None
    )
    return SolArkToken(
        access_token=data["access_token"],
        refresh_token=data.get("refresh_token"),
        expires_in=expires_in,
        scope=data.get("scope"),
        token_type=data.get("token_type"),
        expires_at=expires_at,
        raw=payload,
    )



def parse_user_response(payload: dict[str, Any]) -> SolArkUser:
    data = _unwrap(payload)
    return SolArkUser(
        user_id=data["id"],
        nickname=data.get("nickname"),
        avatar=data.get("avatar"),
        gender=data.get("gender"),
        mobile=data.get("mobile"),
        created_at=_parse_datetime(data.get("createAt")),
        user_type=data.get("type"),
        temp_unit=data.get("tempUnit"),
        company=data.get("company"),
        user_source=data.get("userSrc"),
        company_name=data.get("companyName"),
        company_role=data.get("companyRole"),
        raw=payload,
    )



def parse_realtime_response(payload: dict[str, Any]) -> SolArkRealtime:
    data = _unwrap(payload)
    return SolArkRealtime(
        pac=_parse_float(data.get("pac")),
        etoday=_parse_float(data.get("etoday")),
        emonth=_parse_float(data.get("emonth")),
        eyear=_parse_float(data.get("eyear")),
        etotal=_parse_float(data.get("etotal")),
        income=_parse_float(data.get("income")),
        efficiency=_parse_float(data.get("efficiency")),
        updated_at=_parse_datetime(data.get("updateAt")),
        currency=_parse_currency(data.get("currency")),
        total_power=_parse_float(data.get("totalPower")),
        raw=payload,
    )



def parse_plant_response(payload: dict[str, Any]) -> SolArkPlant:
    data = _unwrap(payload)
    charges = [
        SolArkChargeWindow(
            charge_id=item.get("id"),
            start_range=item.get("startRange"),
            end_range=item.get("endRange"),
            price=_parse_float(item.get("price")),
            charge_type=item.get("type"),
            station_id=item.get("stationId"),
            created_at=_parse_datetime(item.get("createAt")),
            raw=item,
        )
        for item in data.get("charges") or []
    ]
    return SolArkPlant(
        plant_id=data["id"],
        name=data.get("name"),
        total_power=_parse_float(data.get("totalPower")),
        thumb_url=data.get("thumbUrl"),
        join_date=_parse_datetime(data.get("joinDate")),
        plant_type=data.get("type"),
        status=data.get("status"),
        longitude=_parse_float(data.get("lon")),
        latitude=_parse_float(data.get("lat")),
        address=data.get("address"),
        currency=_parse_currency(data.get("currency")),
        timezone=_parse_timezone(data.get("timezone")),
        charges=charges,
        realtime=parse_realtime_response({"code": 0, "data": data.get("realtime", {}), "msg": payload.get("msg")}),
        raw=payload,
    )



def parse_plant_power_response(payload: dict[str, Any], *, collection_key: str | None = None) -> SolArkSeriesCollection:
    data = _unwrap(payload)
    if collection_key:
        series = [
            SolArkSeries(
                label=item.get("label"),
                unit=item.get("unit"),
                records=[_parse_point(record) for record in item.get("records") or []],
                raw=item,
            )
            for item in data.get(collection_key) or []
        ]
        return SolArkSeriesCollection(series=series, raw=payload)
    return SolArkSeriesCollection(
        unit=data.get("unit"),
        records=[_parse_point(record) for record in data.get("records") or []],
        raw=payload,
    )



def parse_energy_flow_response(payload: dict[str, Any]) -> SolArkEnergyFlow:
    data = _unwrap(payload)
    return SolArkEnergyFlow(
        pv_power=_parse_float(data.get("pvPower")),
        battery_power=_parse_float(data.get("battPower")),
        grid_power=_parse_float(data.get("gridOrMeterPower")),
        load_power=_parse_float(data.get("loadOrEpsPower")),
        generator_power=_parse_float(data.get("genPower")),
        microinverter_power=_parse_float(data.get("minPower")),
        soc=_parse_float(data.get("soc")),
        to_load=data.get("toLoad"),
        to_grid=data.get("toGrid"),
        to_battery=data.get("toBat"),
        from_battery=data.get("batTo"),
        from_grid=data.get("gridTo"),
        generator_to=data.get("genTo"),
        exists_generator=data.get("existsGen"),
        exists_microinverter=data.get("existsMin"),
        generator_on=data.get("genOn"),
        microinverter_on=data.get("microOn"),
        exists_meter=data.get("existsMeter"),
        meter_code=data.get("meterCode"),
        bms_comm_fault=data.get("bmsCommFaultFlag"),
        raw=payload,
    )



def parse_generation_use_response(payload: dict[str, Any]) -> SolArkGenerationUse:
    data = _unwrap(payload)
    return SolArkGenerationUse(
        load=_parse_float(data.get("load")),
        pv=_parse_float(data.get("pv")),
        battery_charge=_parse_float(data.get("batteryCharge")),
        grid_sell=_parse_float(data.get("gridSell")),
        raw=payload,
    )



def parse_plant_contacts_response(payload: dict[str, Any]) -> SolArkPlantContacts:
    data = _unwrap(payload)
    return SolArkPlantContacts(
        plant_id=data["id"],
        name=data.get("name"),
        updated_at=_parse_datetime(data.get("updateAt")),
        raw=payload,
    )



def parse_plants_map_response(payload: dict[str, Any]) -> list[SolArkPlantMapPoint]:
    data = _unwrap(payload).get("items", [])
    return [
        SolArkPlantMapPoint(
            plant_id=item["id"],
            longitude=_parse_float(item.get("lon")),
            latitude=_parse_float(item.get("lat")),
            status=item.get("status"),
            raw=item,
        )
        for item in data
    ]



def parse_version_response(payload: dict[str, Any]) -> SolArkVersionInfo:
    data = _unwrap(payload)
    return SolArkVersionInfo(version=data.get("version"), raw=payload)



def parse_device_count_response(payload: dict[str, Any]) -> SolArkDeviceCount:
    data = _unwrap(payload)
    return SolArkDeviceCount(
        total=data.get("total"),
        normal=data.get("normal"),
        warning=data.get("warning"),
        fault=data.get("fault"),
        offline=data.get("offline"),
        updated_at=_parse_datetime(data.get("updateAt")),
        raw=payload,
    )
