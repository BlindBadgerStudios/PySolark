from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class SolArkToken:
    access_token: str
    refresh_token: str | None
    expires_in: int | None
    scope: str | None
    token_type: str | None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class SolArkCurrency:
    currency_id: int | None
    code: str | None
    text: str | None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class SolArkTimezone:
    timezone_id: int | None
    code: str | None
    text: str | None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class SolArkChargeWindow:
    charge_id: int | None
    start_range: str | None
    end_range: str | None
    price: float | None
    charge_type: int | None
    station_id: int | None
    created_at: datetime | None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class SolArkUser:
    user_id: int
    nickname: str | None
    avatar: str | None
    gender: int | None
    mobile: str | None
    created_at: datetime | None
    user_type: str | None
    temp_unit: str | None
    company: str | None
    user_source: str | None
    company_name: str | None
    company_role: str | None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class SolArkRealtime:
    pac: float | None
    etoday: float | None
    emonth: float | None
    eyear: float | None
    etotal: float | None
    income: float | None
    efficiency: float | None
    updated_at: datetime | None
    currency: SolArkCurrency | None
    total_power: float | None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class SolArkPlant:
    plant_id: int
    name: str | None
    total_power: float | None
    thumb_url: str | None
    join_date: datetime | None
    plant_type: int | None
    status: int | None
    longitude: float | None
    latitude: float | None
    address: str | None
    currency: SolArkCurrency | None
    timezone: SolArkTimezone | None
    charges: list[SolArkChargeWindow]
    realtime: SolArkRealtime | None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class SolArkPoint:
    time: str
    value: float | None
    updated_at: datetime | None


@dataclass
class SolArkSeries:
    label: str | None
    unit: str | None
    records: list[SolArkPoint]
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class SolArkSeriesCollection:
    unit: str | None = None
    records: list[SolArkPoint] = field(default_factory=list)
    series: list[SolArkSeries] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class SolArkEnergyFlow:
    pv_power: float | None
    battery_power: float | None
    grid_power: float | None
    load_power: float | None
    generator_power: float | None
    microinverter_power: float | None
    soc: float | None
    to_load: bool | None
    to_grid: bool | None
    to_battery: bool | None
    from_battery: bool | None
    from_grid: bool | None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class SolArkGenerationUse:
    load: float | None
    pv: float | None
    battery_charge: float | None
    grid_sell: float | None
    raw: dict[str, Any] = field(default_factory=dict)
