from __future__ import annotations

import json
import os
from pathlib import Path

from pysolark import SolArkClient
from pysolark.env import load_env_file
from pysolark.smoke import run_smoke_checks



def main() -> None:
    env_path = os.environ.get("SOLARK_ENV_FILE")
    if env_path:
        load_env_file(Path(env_path))

    username = os.environ["SOLARK_EMAIL"]
    password = os.environ["SOLARK_PASSWORD"]
    plant_id = int(os.environ["SOLARK_PLANT_ID"])

    client = SolArkClient(username=username, password=password)
    client.login()
    summary = run_smoke_checks(client, plant_id=plant_id)
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
