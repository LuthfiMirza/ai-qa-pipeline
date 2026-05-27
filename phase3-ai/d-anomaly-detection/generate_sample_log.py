from datetime import datetime, timedelta
from pathlib import Path
import random

LEVELS = ["INFO", "INFO", "INFO", "INFO", "WARNING", "ERROR"]
MODULES = ["auth", "payment", "orders", "inventory", "api", "worker"]
MESSAGES = {
    "INFO": [
        "Request completed successfully response_time_ms={rt}",
        "Background job finished response_time_ms={rt}",
        "Health check passed response_time_ms={rt}",
    ],
    "WARNING": [
        "Slow request detected response_time_ms={rt}",
        "Retrying external service call response_time_ms={rt}",
        "Cache miss rate increased response_time_ms={rt}",
    ],
    "ERROR": [
        "Login failed for user response_time_ms={rt}",
        "Database timeout response_time_ms={rt}",
        "Payment gateway rejected transaction response_time_ms={rt}",
    ],
}


def generate_log(path: str = "sample_logs/app.log", rows: int = 1200) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    start = datetime(2024, 1, 15, 10, 0, 0)
    anomaly_minutes = {180, 181, 420, 421, 422, 900}

    with output_path.open("w", encoding="utf-8") as file:
        for index in range(rows):
            timestamp = start + timedelta(seconds=index * 10)
            minute = index // 6
            module = random.choice(MODULES)

            if minute in anomaly_minutes:
                level = random.choice(["ERROR", "ERROR", "ERROR", "WARNING"])
                response_time = random.randint(1200, 4500)
            else:
                level = random.choice(LEVELS)
                response_time = random.randint(20, 450)

            message = random.choice(MESSAGES[level]).format(rt=response_time)
            file.write(f"{timestamp:%Y-%m-%d %H:%M:%S} {level} [{module}] {message}\n")

    return output_path


if __name__ == "__main__":
    created = generate_log()
    print(f"Generated sample log: {created}")
