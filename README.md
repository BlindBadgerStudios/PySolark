# pysolark

pysolark is a Python client for the Sol-Ark Cloud API.

This library is intentionally validation-first and currently optimized for near-real-time visibility (for time-series systems like Prometheus). Sol-Ark publishes very little public API documentation, so the current framework focuses on endpoints confirmed by direct login tests against `https://api.solarkcloud.com` and by inspecting the `mysolark.com` frontend bundle.

Validated API areas in the current near-real-time-focused cut:
- `POST /oauth/token`
- `GET /api/v1/user`
- `GET /api/v1/plant/{id}`
- `GET /api/v1/plant/{id}/realtime`
- `GET /api/v1/plant/energy/{id}/flow`
- `GET /api/v1/plant/energy/{id}/generation/use`
- `POST /api/v1/plant/{id}/contacts`
- `GET /api/v1/plants/map`
- `GET /api/v1/version/latest`
- `GET /api/v1/batteries/count`
- `GET /api/v1/inverters/count`

Additionally, the library exposes `raw_get()` so we can continue exploring undocumented endpoints safely while still surfacing Sol-Ark envelope errors as `SolArkAPIError`.

## Install

```bash
pip install pysolark
```

## Quick start

```python
from pysolark import SolArkClient

client = SolArkClient(username="you@example.com", password="***")
client.login()

plant_id = 123456  # replace with your Sol-Ark plant ID
plant = client.get_plant(plant_id)
realtime = client.get_plant_realtime(plant_id)
flow = client.get_plant_energy_flow(plant_id)
usage = client.get_plant_generation_use(plant_id)
contacts = client.get_plant_contacts(plant_id)
plants_map = client.get_plants_map()
latest_version = client.get_latest_version()
battery_count = client.get_batteries_count()
inverter_count = client.get_inverters_count()

print(plant.name)
print(realtime.pac)
print(flow.soc)
print(usage.grid_sell)
print(contacts.updated_at)
print(plants_map[0].plant_id if plants_map else None)
print(latest_version.version)
print(battery_count.total, inverter_count.total)
```

## Live smoke check

```bash
SOLARK_ENV_FILE=/path/to/solark-cloud.env ./examples/live_authenticated_smoke.sh
```

Expected output is JSON summarizing a real authenticated pass across the currently validated near-real-time endpoints.

## Notes

Observed authentication behavior:
- login succeeds with JSON body fields `grant_type=password`, `username=<email>`, and `password=<password>`
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

## Roadmap

- Keep the client centered on near-real-time plant, flow, battery, and device-status visibility
- Add convenience helpers for exporter-friendly near-real-time telemetry shaping
- Revisit historical/day-month-year data pulls later, after the near-real-time surface is stable
