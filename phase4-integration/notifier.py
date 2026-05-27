from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any


def _get_value(result: Any, key: str, default: Any = None) -> Any:
    if isinstance(result, dict):
        return result.get(key, default)
    return getattr(result, key, default)


def notify(results: list[Any], report_path: str) -> None:
    pass_count = sum(1 for result in results if _get_value(result, "status") == "PASS")
    fail_count = sum(1 for result in results if _get_value(result, "status") == "FAIL")
    skip_count = sum(1 for result in results if _get_value(result, "status") == "SKIP")

    lines = [
        "STEP              STATUS    DURATION",
        "─────────────────────────────────────",
    ]
    for result in results:
        name = str(_get_value(result, "name", ""))[:17]
        status = str(_get_value(result, "status", ""))
        duration = float(_get_value(result, "duration_sec", 0.0))
        lines.append(f"{name:<17} {status:<8} {duration:.1f}s")
    lines.extend(
        [
            "─────────────────────────────────────",
            f"TOTAL: {pass_count} PASS, {fail_count} FAIL, {skip_count} SKIP",
            f"REPORT: {report_path}",
        ]
    )

    output = "\n".join(lines)
    print(output)
    send_report_instructions(report_path)

    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    (log_dir / f"pipeline_{timestamp}.log").write_text(output + "\n", encoding="utf-8")


def send_report_instructions(report_path: str) -> None:
    path = Path(report_path)
    size_kb = path.stat().st_size / 1024 if path.exists() else 0.0
    print(f"Report ready: {report_path}")
    print(f"File size  : {size_kb:.1f} KB")
    print("Share via  : attach to email or upload to Google Drive")
