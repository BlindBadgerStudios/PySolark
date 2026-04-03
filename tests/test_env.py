import os
from pathlib import Path

from pysolark.env import load_env_file

TEST_USERNAME = "operator@example.com"
TEST_PASSWORD = "secret"
TEST_PLANT_ID = "424242"


def test_load_env_file_accepts_export_prefix(tmp_path: Path, monkeypatch):
    env_file = tmp_path / "solark.env"
    env_file.write_text(
        "# comment\n"
        f"export SOLARK_EMAIL={TEST_USERNAME}\n"
        f"export SOLARK_PASSWORD={TEST_PASSWORD}\n"
        f'SOLARK_PLANT_ID="{TEST_PLANT_ID}"\n'
    )

    monkeypatch.delenv("SOLARK_EMAIL", raising=False)
    monkeypatch.delenv("SOLARK_PASSWORD", raising=False)
    monkeypatch.delenv("SOLARK_PLANT_ID", raising=False)

    load_env_file(env_file)

    assert os.environ["SOLARK_EMAIL"] == TEST_USERNAME
    assert os.environ["SOLARK_PASSWORD"] == TEST_PASSWORD
    assert os.environ["SOLARK_PLANT_ID"] == TEST_PLANT_ID
