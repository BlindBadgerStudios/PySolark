import os
from pathlib import Path

from pysolark.env import load_env_file



def test_load_env_file_accepts_export_prefix(tmp_path: Path, monkeypatch):
    env_file = tmp_path / "solark.env"
    env_file.write_text(
        "# comment\n"
        "export SOLARK_EMAIL=user@example.com\n"
        "export SOLARK_PASSWORD=secret\n"
        "SOLARK_PLANT_ID=\"424242\"\n"
    )

    monkeypatch.delenv("SOLARK_EMAIL", raising=False)
    monkeypatch.delenv("SOLARK_PASSWORD", raising=False)
    monkeypatch.delenv("SOLARK_PLANT_ID", raising=False)

    load_env_file(env_file)

    assert os.environ["SOLARK_EMAIL"] == "user@example.com"
    assert os.environ["SOLARK_PASSWORD"] == "secret"
    assert os.environ["SOLARK_PLANT_ID"] == "424242"
