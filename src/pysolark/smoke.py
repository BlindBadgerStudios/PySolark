from __future__ import annotations

from typing import Any



def run_smoke_checks(client: Any, *, plant_id: int) -> dict[str, Any]:
    user = client.get_current_user()
    plant = client.get_plant(plant_id)
    realtime = client.get_plant_realtime(plant_id)
    flow = client.get_plant_energy_flow(plant_id)
    map_points = client.get_plants_map()
    contacts = client.get_plant_contacts(plant_id)
    version = client.get_latest_version()
    batteries = client.get_batteries_count()
    inverters = client.get_inverters_count()

    return {
        "user_id": user.user_id,
        "plant_name": plant.name,
        "realtime_pac": realtime.pac,
        "battery_soc": flow.soc,
        "map_points": len(map_points),
        "contacts_updated_at": contacts.updated_at,
        "latest_version": version.version,
        "battery_total": batteries.total,
        "inverter_total": inverters.total,
    }
