from __future__ import annotations

import argparse
import html
import json
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from notifier import Notifier

STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
STATUS_SKIP = "SKIP"


@dataclass
class StepResult:
    name: str
    status: str
    duration: float
    command: list[str]
    output_path: str | None = None
    message: str = ""
    returncode: int | None = None
    stdout: str = ""
    stderr: str = ""


class QAPipeline:
    def __init__(self, config_path: str | Path, dry_run: bool = False):
        self.root_dir = Path(__file__).resolve().parents[1]
        self.phase4_dir = Path(__file__).resolve().parent
        self.config_path = Path(config_path)
        self.config = self.load_config(self.config_path)
        self.dry_run = dry_run
        self.results: list[StepResult] = []
        self.report_dir = self._resolve_phase4_path(self.config["paths"].get("report_dir", "reports"))
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.notifier = Notifier(self.phase4_dir / "logs" / "pipeline_notifications.log")

    @staticmethod
    def load_config(yaml_path: str | Path) -> dict[str, Any]:
        path = Path(yaml_path)
        with path.open("r", encoding="utf-8") as file:
            config = yaml.safe_load(file) or {}
        config.setdefault("target_urls", [])
        config.setdefault("thresholds", {})
        config.setdefault("paths", {})
        config.setdefault("steps", {})
        return config

    def _resolve_root_path(self, path: str | Path) -> Path:
        raw_path = Path(path)
        if raw_path.is_absolute():
            return raw_path
        return (self.phase4_dir / raw_path).resolve()

    def _resolve_phase4_path(self, path: str | Path) -> Path:
        raw_path = Path(path)
        if raw_path.is_absolute():
            return raw_path
        return (self.phase4_dir / raw_path).resolve()

    def _record_skip(self, name: str, message: str, command: list[str] | None = None) -> StepResult:
        result = StepResult(name=name, status=STATUS_SKIP, duration=0.0, command=command or [], message=message)
        self.results.append(result)
        self.notifier.notify(f"{name}: {message}", level="WARNING")
        return result

    def _run_subprocess(self, name: str, command: list[str], cwd: Path, output_path: str | Path | None = None) -> StepResult:
        if self.dry_run:
            result = StepResult(
                name=name,
                status=STATUS_SKIP,
                duration=0.0,
                command=command,
                output_path=str(output_path) if output_path else None,
                message=f"Dry-run: would execute in {cwd}",
            )
            self.results.append(result)
            self.notifier.notify(f"DRY-RUN {name}: {' '.join(command)}")
            return result

        if not cwd.exists():
            return self._record_skip(name, f"Working directory not found: {cwd}", command)

        started = time.perf_counter()
        completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
        duration = time.perf_counter() - started
        status = STATUS_PASS if completed.returncode == 0 else STATUS_FAIL
        result = StepResult(
            name=name,
            status=status,
            duration=duration,
            command=command,
            output_path=str(output_path) if output_path else None,
            message="Command completed" if status == STATUS_PASS else "Command failed",
            returncode=completed.returncode,
            stdout=completed.stdout[-4000:],
            stderr=completed.stderr[-4000:],
        )
        self.results.append(result)
        self.notifier.notify(f"{name}: {status} in {duration:.2f}s", level="INFO" if status == STATUS_PASS else "ERROR")
        return result

    def step_generate_tests(self, requirement_text: str) -> StepResult:
        if not self.config["steps"].get("run_test_generation", True):
            return self._record_skip("Generate Tests", "Disabled by config")

        phase_dir = self.root_dir / "phase3-ai" / "a-test-generation"
        generator = phase_dir / "generator.py"
        prompt_builder = phase_dir / "prompt_builder.py"
        script = generator if generator.exists() else prompt_builder
        output_path = phase_dir / "examples" / "generated_tests"

        if self.dry_run:
            command = [sys.executable, script.name, requirement_text]
            return self._run_subprocess("Generate Tests", command, phase_dir, output_path)

        if not script.exists():
            return self._record_skip("Generate Tests", f"Generator script not found: {generator} or {prompt_builder}")

        command = [sys.executable, script.name, requirement_text]
        return self._run_subprocess("Generate Tests", command, phase_dir, output_path)

    def step_run_tests(self) -> StepResult:
        phase_dir = self.root_dir / "phase2-automation"
        output_path = phase_dir / "reports"
        command = [sys.executable, "-m", "pytest", str(phase_dir)]

        if self.dry_run:
            return self._run_subprocess("Run Tests", command, self.root_dir, output_path)

        if not phase_dir.exists():
            return self._record_skip("Run Tests", f"Phase 2 folder not found: {phase_dir}")

        return self._run_subprocess("Run Tests", command, self.root_dir, output_path)

    def step_visual_regression(self) -> StepResult:
        if not self.config["steps"].get("run_visual", True):
            return self._record_skip("Visual Regression", "Disabled by config")

        phase_dir = self.root_dir / "phase3-ai" / "b-visual-regression"
        runner = phase_dir / "screenshot_runner.py"

        target_urls = self.config.get("target_urls", [])
        first_url = target_urls[0] if target_urls else "https://example.com"
        output_path = phase_dir / "reports"
        command = [sys.executable, runner.name, "--url", first_url, "--mode", "compare"]

        if self.dry_run:
            return self._run_subprocess("Visual Regression", command, phase_dir, output_path)

        if not runner.exists():
            return self._record_skip("Visual Regression", f"Runner script not found: {runner}")

        return self._run_subprocess("Visual Regression", command, phase_dir, output_path)

    def step_anomaly_detection(self, log_path: str | Path | None = None) -> StepResult:
        if not self.config["steps"].get("run_anomaly", True):
            return self._record_skip("Anomaly Detection", "Disabled by config")

        phase_dir = self.root_dir / "phase3-ai" / "d-anomaly-detection"
        detector = phase_dir / "anomaly_detector.py"

        configured_log_dir = self._resolve_root_path(self.config["paths"].get("log_dir", "../phase3-ai/d-anomaly-detection/sample_logs"))
        selected_log = Path(log_path) if log_path else configured_log_dir / "app.log"
        if not selected_log.is_absolute():
            selected_log = (self.phase4_dir / selected_log).resolve()
        output_path = phase_dir / "reports"
        command = [sys.executable, detector.name, "--log", str(selected_log)]

        if self.dry_run:
            return self._run_subprocess("Anomaly Detection", command, phase_dir, output_path)

        if not detector.exists():
            return self._record_skip("Anomaly Detection", f"Detector script not found: {detector}")

        return self._run_subprocess("Anomaly Detection", command, phase_dir, output_path)

    def step_generate_report(self) -> StepResult:
        started = time.perf_counter()
        report_path = self.report_dir / "unified_pipeline_report.html"
        dashboard_path = self.phase4_dir / "dashboard" / "index.html"
        dashboard_path.parent.mkdir(parents=True, exist_ok=True)

        summary = self._summary_counts()
        html_content = self._render_report(summary)
        report_path.write_text(html_content, encoding="utf-8")
        dashboard_path.write_text(html_content, encoding="utf-8")

        result = StepResult(
            name="Generate Unified Report",
            status=STATUS_PASS,
            duration=time.perf_counter() - started,
            command=[],
            output_path=str(report_path),
            message=f"Dashboard updated: {dashboard_path}",
        )
        self.results.append(result)
        self.notifier.notify(f"Unified report generated: {report_path}")
        return result

    def _summary_counts(self) -> dict[str, int]:
        pass_count = sum(1 for result in self.results if result.status == STATUS_PASS)
        fail_count = sum(1 for result in self.results if result.status == STATUS_FAIL)
        skip_count = sum(1 for result in self.results if result.status == STATUS_SKIP)
        return {
            "total": len(self.results),
            "passed": pass_count,
            "failed": fail_count,
            "skipped": skip_count,
        }

    def _render_report(self, summary: dict[str, int]) -> str:
        rows = []
        for result in self.results:
            css_class = result.status.lower()
            command = " ".join(result.command) if result.command else "-"
            output = result.output_path or "-"
            output_cell = f'<a href="{html.escape(output)}">{html.escape(output)}</a>' if output != "-" else "-"
            rows.append(
                "<tr>"
                f'<td>{html.escape(result.name)}</td>'
                f'<td><span class="status {css_class}">{html.escape(result.status)}</span></td>'
                f"<td>{result.duration:.2f}s</td>"
                f"<td>{output_cell}</td>"
                f"<td><code>{html.escape(command)}</code><br>{html.escape(result.message)}</td>"
                "</tr>"
            )

        generated_at = datetime.now().isoformat(timespec="seconds")
        return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AI-Assisted QA Pipeline Dashboard</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 32px; color: #1f2937; background: #f8fafc; }}
    h1, h2 {{ color: #111827; }}
    .summary {{ display: grid; grid-template-columns: repeat(4, minmax(120px, 1fr)); gap: 12px; margin: 20px 0; }}
    .card {{ background: #fff; border: 1px solid #e5e7eb; border-radius: 10px; padding: 16px; }}
    .value {{ font-size: 28px; font-weight: 700; }}
    table {{ width: 100%; border-collapse: collapse; background: #fff; }}
    th, td {{ border: 1px solid #e5e7eb; padding: 10px; vertical-align: top; }}
    th {{ background: #f3f4f6; text-align: left; }}
    code, pre {{ background: #111827; color: #f9fafb; border-radius: 6px; padding: 2px 5px; }}
    pre {{ padding: 16px; overflow-x: auto; }}
    .status {{ color: #fff; border-radius: 999px; padding: 4px 10px; font-weight: 700; }}
    .pass {{ background: #16a34a; }}
    .fail {{ background: #dc2626; }}
    .skip {{ background: #6b7280; }}
  </style>
</head>
<body>
  <h1>AI-Assisted QA Pipeline Dashboard</h1>
  <p>Generated at {html.escape(generated_at)}</p>

  <h2>Summary</h2>
  <div class="summary">
    <div class="card"><div>Total Steps</div><div class="value">{summary['total']}</div></div>
    <div class="card"><div>Pass</div><div class="value">{summary['passed']}</div></div>
    <div class="card"><div>Fail</div><div class="value">{summary['failed']}</div></div>
    <div class="card"><div>Skip</div><div class="value">{summary['skipped']}</div></div>
  </div>

  <h2>Step Results</h2>
  <table>
    <thead><tr><th>Step</th><th>Status</th><th>Duration</th><th>Detail Report</th><th>Command / Message</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table>

  <h2>Cara Eksekusi Manual</h2>
  <pre>cd phase3-ai/a-test-generation && python prompt_builder.py --input examples/input_requirements.txt --output examples/exported_prompt.md
cd phase2-automation && pytest
cd phase3-ai/b-visual-regression && python screenshot_runner.py --url https://example.com --mode compare
cd phase3-ai/d-anomaly-detection && python anomaly_detector.py --log sample_logs/app.log
cd phase4-integration && python pipeline.py --config pipeline_config.yaml</pre>
</body>
</html>
"""

    def run_all(self) -> dict[str, Any]:
        self.notifier.notify("Starting AI-assisted QA pipeline")
        requirement_text = "User can login with valid credentials and sees an error for invalid credentials."
        self.step_generate_tests(requirement_text)
        self.step_run_tests()
        self.step_visual_regression()
        self.step_anomaly_detection()
        self.step_generate_report()

        summary = self._summary_counts()
        summary["results"] = [asdict(result) for result in self.results]
        self.notifier.summary(summary)
        return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the full AI-assisted QA pipeline")
    parser.add_argument("--config", default="pipeline_config.yaml", help="Path to pipeline YAML config")
    parser.add_argument("--dry-run", action="store_true", help="Print planned steps without executing subprocesses")
    args = parser.parse_args()

    pipeline = QAPipeline(config_path=args.config, dry_run=args.dry_run)
    summary = pipeline.run_all()
    print(json.dumps({key: value for key, value in summary.items() if key != "results"}, indent=2))


if __name__ == "__main__":
    main()
