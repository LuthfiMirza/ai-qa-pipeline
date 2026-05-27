from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any


class Notifier:
    def __init__(self, log_path: str | Path = "logs/pipeline_notifications.log"):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def notify(self, message: str, level: str = "INFO") -> None:
        timestamp = datetime.now().isoformat(timespec="seconds")
        line = f"[{timestamp}] {level.upper()} {message}"
        print(line)
        with self.log_path.open("a", encoding="utf-8") as file:
            file.write(line + "\n")

    def summary(self, summary: dict[str, Any]) -> None:
        total = summary.get("total", 0)
        passed = summary.get("passed", 0)
        failed = summary.get("failed", 0)
        skipped = summary.get("skipped", 0)
        self.notify(f"Pipeline summary: total={total}, pass={passed}, fail={failed}, skip={skipped}")
