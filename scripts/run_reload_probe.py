from __future__ import annotations

import argparse
import asyncio
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from teleapp import build_runtime_config
from teleapp.supervisor import AppSupervisor


async def _probe_reload(app_path: Path) -> None:
    config = build_runtime_config(
        app_path=app_path,
        hot_reload=True,
        reload_quiet_seconds=1,
        reload_poll_seconds=1,
        auto_restart_on_crash=False,
    )
    supervisor = AppSupervisor(config)
    await supervisor.start()
    original_pid = supervisor.state.pid
    await supervisor.restart("manual probe restart")
    new_pid = supervisor.state.pid
    await supervisor.stop()

    if original_pid == new_pid:
        raise SystemExit("Reload probe failed: pid did not change after restart.")

    print(f"Reload probe succeeded: {original_pid} -> {new_pid}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--app", default="examples/echo_app.py")
    args = parser.parse_args()
    asyncio.run(_probe_reload(Path(args.app).resolve()))


if __name__ == "__main__":
    main()
