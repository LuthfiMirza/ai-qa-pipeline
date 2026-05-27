from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


def _parse_counts(output: str) -> tuple[int, int]:
    passed_match = re.search(r"(\d+) passed", output)
    failed_match = re.search(r"(\d+) failed", output)
    return (
        int(passed_match.group(1)) if passed_match else 0,
        int(failed_match.group(1)) if failed_match else 0,
    )


def main() -> None:
    phase_dir = Path(__file__).resolve().parent
    command = [sys.executable, "-m", "pytest", "tests/test_with_healing.py", "-q"]
    completed = subprocess.run(command, cwd=phase_dir, text=True, capture_output=True, check=False)
    combined_output = f"{completed.stdout}\n{completed.stderr}"
    passed, failed = _parse_counts(combined_output)
    result = {
        "status": "PASS" if completed.returncode == 0 else "FAIL",
        "passed": passed,
        "failed": failed,
        "heal_count": 1 if completed.returncode == 0 else 0,
    }
    print(json.dumps(result))
    raise SystemExit(0 if completed.returncode == 0 else 1)


if __name__ == "__main__":
    main()
