#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [ ! -x ".venv/bin/python" ]; then
  echo "Missing .venv. Run bootstrap_teleapp.sh first."
  exit 1
fi

. .venv/bin/activate

if [ "$#" -eq 0 ]; then
  exec teleapp
else
  exec teleapp "$@"
fi
