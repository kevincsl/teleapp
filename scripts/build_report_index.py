from __future__ import annotations

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def build_index(report_dir: Path) -> tuple[Path, dict]:
    report_dir.mkdir(parents=True, exist_ok=True)
    entries: list[dict] = []

    for path in sorted(report_dir.glob("*.json")):
        if path.name == "index.json":
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue

        entries.append(
            {
                "file": path.name,
                "kind": payload.get("kind"),
                "generated_at": payload.get("generated_at"),
                "passed": payload.get("passed"),
                "requests": payload.get("requests"),
                "chats": payload.get("chats"),
                "duration_seconds": payload.get("duration_seconds"),
            }
        )

    index = {
        "kind": "teleapp_report_index",
        "report_count": len(entries),
        "entries": entries,
    }
    index_path = report_dir / "index.json"
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")

    md_lines = [
        "# teleapp Reports Index",
        "",
        f"- report_count: {len(entries)}",
        "",
        "## Reports",
        "",
    ]
    for entry in entries:
        md_lines.append(
            f"- {entry['file']}: kind={entry['kind']} passed={entry['passed']} "
            f"requests={entry['requests']} chats={entry['chats']} duration_seconds={entry['duration_seconds']}"
        )
    (report_dir / "README.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    return index_path, index


def main() -> None:
    report_dir = (PROJECT_ROOT / "reports").resolve()
    index_path, index = build_index(report_dir)
    print(f"Built report index at {index_path} ({index['report_count']} reports)")


if __name__ == "__main__":
    main()
