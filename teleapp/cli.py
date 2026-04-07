from __future__ import annotations

import sys

from teleapp.app import TeleApp
from teleapp.scaffold import create_project


def main() -> None:
    if len(sys.argv) >= 3 and sys.argv[1] == "init":
        target = create_project(sys.argv[2])
        print(f"Created teleapp project at {target}")
        return
    TeleApp.from_cli().run_polling()
