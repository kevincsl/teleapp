from __future__ import annotations

import json
import sys

# Example: subprocess-mode echo app.
# Purpose:
# - demonstrates the JSONL stdin/stdout contract
# - used by runtime tests, soak tests, and restart probes
#
# Start:
# - python -m teleapp examples/echo_app.py --token <token> --allowed-user-id <id>
# - start_teleapp.bat examples/echo_app.py
#
# Stop:
# - stop the running teleapp process in the terminal, or send Ctrl+C
# - if running from Telegram, /restart restarts the runtime but does not "stop" it
#
# Note:
# - this file is intentionally not Flask-like
# - it should remain a pure subprocess contract example


def main() -> None:
    # Read one JSON object per line from stdin and reply with one JSON object per line.
    for line in sys.stdin:
        cleaned = line.strip()
        if not cleaned:
            continue

        try:
            payload = json.loads(cleaned)
        except json.JSONDecodeError:
            # Report malformed input without crashing the hosted app.
            print(json.dumps({"type": "error", "text": "invalid json input"}), flush=True)
            continue

        text = str(payload.get("text") or "")
        chat_id = payload.get("chat_id")
        request_id = payload.get("request_id")
        # Echo the input text back through the runtime event schema.
        print(
            json.dumps(
                {
                    "type": "output",
                    "chat_id": chat_id,
                    "request_id": request_id,
                    "text": f"echo: {text}",
                },
                ensure_ascii=False,
            ),
            flush=True,
        )


if __name__ == "__main__":
    main()
