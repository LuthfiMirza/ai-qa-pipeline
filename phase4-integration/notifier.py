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

    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    (log_dir / f"pipeline_{timestamp}.log").write_text(output + "\n", encoding="utf-8")
