from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
import random

LEVELS = ["INFO", "INFO", "INFO", "INFO", "WARNING", "ERROR"]
MODULES = ["auth", "payment", "orders", "inventory", "api", "worker"]
INFO_MESSAGES = [
    "Request completed in {rt}ms",
    "Background job finished in {rt}ms",
    "Health check passed {rt}ms",
]
WARNING_MESSAGES = [
    "Slow request detected in {rt}ms",
    "Retrying external service call after {rt}ms",
    "Cache miss rate increased, response took {rt}ms",
]
ERROR_MESSAGES = [
    "Login failed for user in {rt}ms",
    "Database timeout after {rt}ms",
    "Payment gateway rejected transaction in {rt}ms",
]


def generate_log(path: str = "sample_logs/app.log", rows: int = 2000) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    start = datetime(2024, 1, 15, 10, 0, 0)
    anomaly_minutes = {45, 46, 120, 121, 122, 240, 241, 300}

    random.seed(42)
    with output_path.open("w", encoding="utf-8") as file:
        for index in range(rows):
            timestamp = start + timedelta(seconds=index * 10)
            minute = index // 6
            module = random.choice(MODULES)

            if minute in anomaly_minutes:
                level = random.choice(["ERROR", "ERROR", "ERROR", "WARNING"])
                response_time = random.randint(1500, 5000)
            else:
                level = random.choice(LEVELS)
                response_time = random.randint(20, 600)

            if level == "ERROR":
                message = random.choice(ERROR_MESSAGES).format(rt=response_time)
            elif level == "WARNING":
                message = random.choice(WARNING_MESSAGES).format(rt=response_time)
            else:
                message = random.choice(INFO_MESSAGES).format(rt=response_time)

            file.write(f"{timestamp:%Y-%m-%d %H:%M:%S} {level} [{module}] {message}\n")

    return output_path


if __name__ == "__main__":
    created = generate_log()
    line_count = sum(1 for _ in created.open("r", encoding="utf-8"))
    print(f"Generated sample log: {created} ({line_count} lines)")
