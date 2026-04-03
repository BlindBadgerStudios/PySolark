# pysolark

pysolark is a Python client for the Sol-Ark Cloud API.

This library is intentionally validation-first. Sol-Ark publishes very little public API documentation, so the current framework focuses on endpoints that were confirmed by direct login tests against `https://api.solarkcloud.com` and by inspecting the `mysolark.com` frontend bundle.

Validated API areas in this first cut:
- `POST /oauth/token`
- `GET /api/v1/user`
- `GET /api/v1/plant/{id}`
- `GET /api/v1/plant/{id}/realtime`
- `GET /api/v1/plant/{id}/power/{day|month|year|total}`
- `GET /api/v1/plant/energy/{id}/{day|month|year|total}`
- `GET /api/v1/plant/energy/{id}/flow`
- `GET /api/v1/plant/energy/{id}/generation/use`
- `GET /api/v1/plant/energy/aggregate`
- `POST /api/v1/plant/{id}/contacts`
- `GET /api/v1/plants/map`
- `GET /api/v1/version/latest`
- `GET /api/v1/batteries/count`
- `GET /api/v1/inverters/count`

Additionally, the library exposes `raw_get()` so we can continue exploring undocumented endpoints safely while still surfacing Sol-Ark envelope errors as `SolArkAPIError`.

## Install

```bash
pip install -e .
```

## Quick start

```python
from pysolark import SolArkClient

client = SolArkClient(username="you@example.com", password="***")
client.login()

plant = client.get_plant(424242)
realtime = client.get_plant_realtime(424242)
power = client.get_plant_power(424242, period="day", date="2026-04-03")
energy = client.get_plant_energy(424242, period="month", date="2026-04")
flow = client.get_plant_energy_flow(424242)
usage = client.get_plant_generation_use(424242)
contacts = client.get_plant_contacts(424242)
plants_map = client.get_plants_map()
latest_version = client.get_latest_version()
battery_count = client.get_batteries_count()
inverter_count = client.get_inverters_count()
report = client.download_plant_energy_aggregate([424242], start_date="2026-04-01", end_date="2026-04-03")

print(plant.name)
print(realtime.pac)
print(power.records[0].value)
print(energy.series[0].label)
print(flow.soc)
print(usage.grid_sell)
print(contacts.updated_at)
print(plants_map[0].plant_id if plants_map else None)
print(latest_version.version)
print(battery_count.total, inverter_count.total)
print(report[:120])
```

## Live smoke check

```bash
SOLARK_ENV_FILE=/path/to/solark-cloud.env ./examples/live_authenticated_smoke.sh
```

Expected output is JSON summarizing a real authenticated pass across the currently validated endpoints.

## Notes

Observed authentication behavior:
- login succeeds with JSON body fields `grant_type=password`, `username=<email>`, `password=<password>`
- the API returns a JSON envelope with `code`, `msg`, `data`, and often `success`
- nonzero `code` values should be treated as API-level failures even when the HTTP status is `200`

Observed documentation gap:
- some endpoints referenced by the frontend still returned `400`, `404`, or `No Permissions` during exploration
- this repo should expand only as additional endpoints are actually validated against live responses

## Development

```bash
uv venv .venv
. .venv/bin/activate
uv pip install -e '.[dev]'
python -m pytest -q
```

## PyPI-ready validation

```bash
. .venv/bin/activate
python -m build
python -m twine check dist/*
```
