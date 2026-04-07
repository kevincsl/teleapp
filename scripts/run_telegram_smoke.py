from __future__ import annotations

import os
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main() -> None:
    required = {
        "TELEAPP_TOKEN": os.getenv("TELEAPP_TOKEN", "").strip(),
        "TELEAPP_ALLOWED_USER_ID": os.getenv("TELEAPP_ALLOWED_USER_ID", "").strip(),
        "TELEAPP_APP": os.getenv("TELEAPP_APP", "").strip(),
    }
    missing = [key for key, value in required.items() if not value]
    if missing:
        raise SystemExit(f"Missing required environment variables: {', '.join(missing)}")

    app_path = Path(required["TELEAPP_APP"]).expanduser().resolve()
    if not app_path.exists():
        raise SystemExit(f"Hosted app not found: {app_path}")

    print("Telegram smoke prerequisites look valid.")
    print(f"TELEAPP_ALLOWED_USER_ID={required['TELEAPP_ALLOWED_USER_ID']}")
    print(f"TELEAPP_APP={app_path}")
    print("Next step: run `start_teleapp.bat` or `./start_teleapp.sh` and send a test message from Telegram.")


if __name__ == "__main__":
    main()
