from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pandas as pd

LOG_PATTERN = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+"
    r"(?P<level>[A-Z]+)\s+"
    r"\[(?P<module>[^\]]+)\]\s*"
    r"(?P<message>.*)$"
)
RESPONSE_TIME_PATTERN = re.compile(r"(?:response[_\s-]?time(?:_ms)?|rt|duration(?:_ms)?)\s*[=:]\s*(?P<value>\d+(?:\.\d+)?)", re.IGNORECASE)


def _extract_response_time(message: str) -> float | None:
    match = RESPONSE_TIME_PATTERN.search(message)
    if not match:
        return None
    return float(match.group("value"))


def parse_log_file(path: str | Path) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    log_path = Path(path)

    with log_path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            raw_line = line.strip()
            if not raw_line:
                continue

            match = LOG_PATTERN.match(raw_line)
            if not match:
                rows.append(
                    {
                        "timestamp": pd.NaT,
                        "level": "UNKNOWN",
                        "module": "unknown",
                        "message": raw_line,
                        "response_time_ms": None,
                        "line_number": line_number,
                    }
                )
                continue

            message = match.group("message")
            rows.append(
                {
                    "timestamp": pd.to_datetime(match.group("timestamp")),
                    "level": match.group("level"),
                    "module": match.group("module"),
                    "message": message,
                    "response_time_ms": _extract_response_time(message),
                    "line_number": line_number,
                }
            )

    df = pd.DataFrame(rows, columns=["timestamp", "level", "module", "message", "response_time_ms", "line_number"])
    if not df.empty:
        df = df.sort_values("timestamp", na_position="last").reset_index(drop=True)
    return df


def get_summary(df: pd.DataFrame) -> dict[str, float | int]:
    total = int(len(df))
    errors = int((df["level"] == "ERROR").sum()) if total else 0
    warnings = int((df["level"] == "WARNING").sum()) if total else 0
    return {
        "total": total,
        "errors": errors,
        "warnings": warnings,
        "error_rate": errors / total if total else 0.0,
    }
