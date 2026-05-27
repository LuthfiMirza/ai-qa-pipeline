from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

LOG_PATTERN = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+"
    r"(?P<level>[A-Z]+)\s+"
    r"\[(?P<module>[^\]]+)\]\s*"
    r"(?P<message>.*)$"
)
RESPONSE_TIME_PATTERN = re.compile(r"(?:in\s+)?(?P<value>\d+(?:\.\d+)?)ms\b", re.IGNORECASE)


def _extract_response_time(message: str) -> float:
    match = RESPONSE_TIME_PATTERN.search(message)
    if not match:
        return float("nan")
    return float(match.group("value"))


def parse_log_file(path: str) -> pd.DataFrame:
    rows = []
    with Path(path).open("r", encoding="utf-8") as file:
        for line in file:
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
                        "response_time_ms": float("nan"),
                    }
                )
                continue

            message = match.group("message")
            rows.append(
                {
                    "timestamp": pd.to_datetime(match.group("timestamp")),
                    "level": str(match.group("level")),
                    "module": str(match.group("module")),
                    "message": str(message),
                    "response_time_ms": _extract_response_time(message),
                }
            )

    df = pd.DataFrame(rows, columns=["timestamp", "level", "module", "message", "response_time_ms"])
    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["level"] = df["level"].astype(str)
        df["module"] = df["module"].astype(str)
        df["message"] = df["message"].astype(str)
        df["response_time_ms"] = df["response_time_ms"].astype(float)
        df = df.sort_values("timestamp", na_position="last").reset_index(drop=True)
    return df


def get_summary(df: pd.DataFrame) -> dict[str, object]:
    total = int(len(df))
    errors = int((df["level"] == "ERROR").sum()) if total else 0
    warnings = int((df["level"] == "WARNING").sum()) if total else 0
    info = int((df["level"] == "INFO").sum()) if total else 0
    valid_timestamps = df["timestamp"].dropna() if total else pd.Series(dtype="datetime64[ns]")
    if valid_timestamps.empty:
        time_range = None
    else:
        time_range = f"{valid_timestamps.min()} - {valid_timestamps.max()}"

    return {
        "total": total,
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "error_rate": errors / total if total else 0.0,
        "time_range": time_range,
    }
