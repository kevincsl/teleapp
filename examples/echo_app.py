from __future__ import annotations

import json
import sys


def main() -> None:
    for line in sys.stdin:
        cleaned = line.strip()
        if not cleaned:
            continue

        try:
            payload = json.loads(cleaned)
        except json.JSONDecodeError:
            print(json.dumps({"type": "error", "text": "invalid json input"}), flush=True)
            continue

        text = str(payload.get("text") or "")
        chat_id = payload.get("chat_id")
        request_id = payload.get("request_id")
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
