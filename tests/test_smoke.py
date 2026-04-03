from pysolark.smoke import run_smoke_checks

TEST_USER_ID = 10101
TEST_PLANT_ID = 424242
TEST_USERNAME = "operator@example.com"
TEST_PLANT_NAME = "Example Plant"


class FakeClient:
    def __init__(self):
        self.calls = []

    def get_current_user(self):
        self.calls.append(("get_current_user", None))
        return type("User", (), {"user_id": TEST_USER_ID, "nickname": TEST_USERNAME})()

    def get_plant(self, plant_id: int):
        self.calls.append(("get_plant", plant_id))
        return type("Plant", (), {"plant_id": plant_id, "name": TEST_PLANT_NAME})()

    def get_plant_realtime(self, plant_id: int):
        self.calls.append(("get_plant_realtime", plant_id))
        return type("Realtime", (), {"pac": 8701, "soc": None})()

    def get_plant_energy_flow(self, plant_id: int):
        self.calls.append(("get_plant_energy_flow", plant_id))
        return type("Flow", (), {"soc": 100.0, "to_grid": True})()

    def get_plants_map(self):
        self.calls.append(("get_plants_map", None))
        return [type("Point", (), {"plant_id": TEST_PLANT_ID, "status": 1})()]

    def get_plant_contacts(self, plant_id: int):
        self.calls.append(("get_plant_contacts", plant_id))
        return type("Contacts", (), {"plant_id": plant_id, "updated_at": "2026-04-03T16:51:16.646+00:00"})()

    def get_latest_version(self):
        self.calls.append(("get_latest_version", None))
        return type("Version", (), {"version": ""})()

    def get_batteries_count(self):
        self.calls.append(("get_batteries_count", None))
        return type("Count", (), {"total": 0})()

    def get_inverters_count(self):
        self.calls.append(("get_inverters_count", None))
        return type("Count", (), {"total": 0})()


def test_run_smoke_checks_returns_summary_for_validated_endpoints():
    client = FakeClient()

    result = run_smoke_checks(client, plant_id=TEST_PLANT_ID)

    assert result["user_id"] == TEST_USER_ID
    assert result["plant_name"] == TEST_PLANT_NAME
    assert result["realtime_pac"] == 8701
    assert result["battery_soc"] == 100.0
    assert result["map_points"] == 1
    assert result["latest_version"] == ""
    assert result["battery_total"] == 0
    assert result["inverter_total"] == 0
    assert client.calls == [
        ("get_current_user", None),
        ("get_plant", TEST_PLANT_ID),
        ("get_plant_realtime", TEST_PLANT_ID),
        ("get_plant_energy_flow", TEST_PLANT_ID),
        ("get_plants_map", None),
        ("get_plant_contacts", TEST_PLANT_ID),
        ("get_latest_version", None),
        ("get_batteries_count", None),
        ("get_inverters_count", None),
    ]
