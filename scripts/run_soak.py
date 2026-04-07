from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
import sys
from datetime import datetime
from time import perf_counter

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from teleapp import TeleApp, build_runtime_config


def _build_report_paths(report_dir: Path) -> tuple[Path, Path]:
    report_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return (
        report_dir / f"soak-report-{stamp}.json",
        report_dir / f"soak-report-{stamp}.md",
    )


def _write_reports(
    *,
    json_path: Path,
    md_path: Path,
    requests: int,
    chats: int,
    duration_seconds: float,
    passed: bool,
    details: dict,
) -> None:
    payload = {
        "kind": "teleapp_soak_report",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "requests": requests,
        "chats": chats,
        "duration_seconds": round(duration_seconds, 3),
        "passed": passed,
        "details": details,
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    md_lines = [
        "# teleapp Soak Report",
        "",
        f"- generated_at: {payload['generated_at']}",
        f"- requests: {requests}",
        f"- chats: {chats}",
        f"- duration_seconds: {payload['duration_seconds']}",
        f"- passed: {'yes' if passed else 'no'}",
        "",
        "## Details",
        "",
    ]
    for key, value in details.items():
        md_lines.append(f"- {key}: {value}")
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")


async def _run_soak(requests: int, chats: int, report_dir: Path) -> None:
    app = TeleApp(build_runtime_config(app_path="examples/echo_app.py", auto_restart_on_crash=False))
    started = perf_counter()
    await app.supervisor.start()

    expected: list[tuple[int, str]] = []
    for index in range(requests):
        chat_id = (index % chats) + 1
        text = f"soak-{index}"
        expected.append((chat_id, f"echo: {text}"))
        await app.supervisor.send_text(chat_id=chat_id, text=text)

    seen: list[tuple[int, str]] = []
    for _ in range(requests):
        event = await asyncio.wait_for(app.supervisor.next_event(), timeout=10)
        seen.append((event.chat_id or 0, event.text))

    await app.supervisor.stop()
    duration_seconds = perf_counter() - started
    json_path, md_path = _build_report_paths(report_dir)

    if seen != expected:
        mismatch_index = next(
            (index for index, pair in enumerate(zip(expected, seen)) if pair[0] != pair[1]),
            min(len(expected), len(seen)),
        )
        details = {
            "result": "mismatch",
            "mismatch_index": mismatch_index,
            "expected_at_mismatch": expected[mismatch_index] if mismatch_index < len(expected) else None,
            "seen_at_mismatch": seen[mismatch_index] if mismatch_index < len(seen) else None,
            "seen_count": len(seen),
        }
        _write_reports(
            json_path=json_path,
            md_path=md_path,
            requests=requests,
            chats=chats,
            duration_seconds=duration_seconds,
            passed=False,
            details=details,
        )
        raise SystemExit(
            f"Soak run failed: observed event sequence does not match expected sequence. Report: {json_path}"
        )

    details = {
        "result": "ok",
        "seen_count": len(seen),
        "final_busy": app.supervisor.state.busy,
        "final_total_queued_requests": app.supervisor.state.total_queued_requests,
    }
    _write_reports(
        json_path=json_path,
        md_path=md_path,
        requests=requests,
        chats=chats,
        duration_seconds=duration_seconds,
        passed=True,
        details=details,
    )
    print(
        f"Soak run completed successfully with {requests} requests across {chats} chats. "
        f"Reports: {json_path}, {md_path}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--requests", type=int, default=100)
    parser.add_argument("--chats", type=int, default=4)
    parser.add_argument("--report-dir", default="reports")
    args = parser.parse_args()
    asyncio.run(
        _run_soak(
            requests=max(1, args.requests),
            chats=max(1, args.chats),
            report_dir=Path(args.report_dir).resolve(),
        )
    )


if __name__ == "__main__":
    main()
