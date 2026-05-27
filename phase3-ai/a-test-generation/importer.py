from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

REQUIRED_FIELDS = ("test_name", "steps", "expected_result")


def _safe_test_name(name: str) -> str:
    safe_name = re.sub(r"[^a-zA-Z0-9_]+", "_", name.strip().lower()).strip("_")
    if not safe_name:
        safe_name = "generated_test"
    if not safe_name.startswith("test_"):
        safe_name = f"test_{safe_name}"
    return safe_name


def _triple_quote(value: str) -> str:
    return value.replace('"""', '\"\"\"')


def validate_json(data: list) -> tuple[bool, list[str]]:
    errors: list[str] = []
    if not isinstance(data, list):
        return False, ["Root JSON must be an array of test cases"]

    for index, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            errors.append(f"Item {index}: must be an object")
            continue

        for field in REQUIRED_FIELDS:
            if field not in item:
                errors.append(f"Item {index}: missing required field '{field}'")

        test_name = item.get("test_name")
        if not isinstance(test_name, str) or not test_name.strip():
            errors.append(f"Item {index}: test_name must be a non-empty string")

        steps = item.get("steps")
        if not isinstance(steps, list) or len(steps) < 1:
            errors.append(f"Item {index}: steps must contain at least 1 step")
        elif not all(isinstance(step, str) and step.strip() for step in steps):
            errors.append(f"Item {index}: every step must be a non-empty string")

        expected_result = item.get("expected_result")
        if not isinstance(expected_result, str) or not expected_result.strip():
            errors.append(f"Item {index}: expected_result must be a non-empty string")

    return len(errors) == 0, errors


def _render_test_case(item: dict[str, Any]) -> str:
    test_name = _safe_test_name(str(item["test_name"]))
    description = str(item.get("description", item.get("desc", "Generated test case")))
    steps = [str(step) for step in item["steps"]]
    expected_result = str(item["expected_result"])
    steps_text = "\n".join(f"    {number}. {step}" for number, step in enumerate(steps, start=1))

    return f'''@pytest.mark.generated
def {test_name}():
    """
    Description:
    {_triple_quote(description)}

    Steps:
{_triple_quote(steps_text)}

    Expected Result:
    {_triple_quote(expected_result)}
    """
    # TODO: Implement executable test steps based on the generated scenario.
    # TODO: Replace this placeholder with real assertions or Playwright actions.
    pass
'''


def _write_pytest_file(data: list[dict[str, Any]], output_path: str) -> str:
    destination = Path(output_path)
    if destination.suffix != ".py":
        destination.mkdir(parents=True, exist_ok=True)
        destination = destination / "test_generated_from_chatgpt.py"
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)

    body = "\n\n".join(_render_test_case(item) for item in data)
    content = f'''"""Generated Pytest skeletons imported from ChatGPT JSON output."""

import pytest


{body}
'''
    destination.write_text(content, encoding="utf-8")
    return str(destination)


def import_from_json(json_path: str, output_path: str) -> str:
    data = json.loads(Path(json_path).read_text(encoding="utf-8"))
    is_valid, errors = validate_json(data)
    if not is_valid:
        raise ValueError("Invalid JSON test cases:\n" + "\n".join(errors))
    return _write_pytest_file(data, output_path)


def import_from_clipboard() -> str:
    raw_input = sys.stdin.read()
    data = json.loads(raw_input)
    is_valid, errors = validate_json(data)
    if not is_valid:
        raise ValueError("Invalid JSON test cases:\n" + "\n".join(errors))
    return _write_pytest_file(data, "examples/generated_tests/test_generated_from_stdin.py")


def main() -> None:
    parser = argparse.ArgumentParser(description="Import ChatGPT JSON test cases into Pytest skeletons")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--file", help="Path to ChatGPT JSON output file")
    source.add_argument("--stdin", action="store_true", help="Read ChatGPT JSON output from stdin")
    parser.add_argument("--output", default="examples/generated_tests/", help="Output .py file or directory")
    args = parser.parse_args()

    if args.stdin:
        output = import_from_clipboard()
    else:
        output = import_from_json(args.file, args.output)

    print(f"Pytest file generated: {output}")


if __name__ == "__main__":
    main()
