from __future__ import annotations

import argparse
import html
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import yaml

from notifier import notify


@dataclass
class StepResult:
    name: str
    status: str
    duration_sec: float
    output: str
    error: str


class QAPipeline:
    def __init__(self, config_path: str):
        self.phase4_dir = Path(__file__).resolve().parent
        self.root_dir = self.phase4_dir.parent
        self.config_path = Path(config_path)
        if not self.config_path.is_absolute():
            self.config_path = (Path.cwd() / self.config_path).resolve()
        self.config = self._load_config(self.config_path)
        self.dry_run = False

    @staticmethod
    def _load_config(config_path: Path) -> dict:
        with config_path.open("r", encoding="utf-8") as file:
            return yaml.safe_load(file) or {}

    def _run_command(self, name: str, command: list[str], cwd: Path) -> StepResult:
        started = time.perf_counter()
        command_text = " ".join(command)

        if self.dry_run:
            print(f"DRY-RUN {name}: cd {cwd} && {command_text}")
            return StepResult(name=name, status="SKIP", duration_sec=0.0, output=command_text, error="dry-run")

        if not cwd.exists():
            return StepResult(name=name, status="FAIL", duration_sec=0.0, output="", error=f"Missing directory: {cwd}")

        try:
            completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
        except OSError as exc:
            return StepResult(name=name, status="FAIL", duration_sec=0.0, output="", error=str(exc))

        duration = time.perf_counter() - started
        status = "PASS" if completed.returncode == 0 else "FAIL"
        return StepResult(
            name=name,
            status=status,
            duration_sec=duration,
            output=completed.stdout[-4000:],
            error=completed.stderr[-4000:],
        )

    def step_generate_tests(self) -> StepResult:
        phase_dir = self.root_dir / "phase3-ai" / "a-test-generation"
        requirement = self.config.get("sample_requirement", "User dapat login dengan email dan password")
        command = [
            sys.executable,
            "generator.py",
            "--requirement",
            requirement,
            "--export-prompt",
            "--json-only",
        ]
        return self._run_command("Generate Tests", command, phase_dir)

    def step_run_unit_tests(self) -> StepResult:
        phase_dir = self.root_dir / "phase1-foundation"
        command = [sys.executable, "-m", "pytest", "tests/test_calculator.py", "-v"]
        return self._run_command("Unit Tests", command, phase_dir)

    def step_visual_regression(self) -> StepResult:
        phase_dir = self.root_dir / "phase3-ai" / "b-visual-regression"
        target_url = self.config.get("target_urls", ["https://example.com"])[0]
        command = [sys.executable, "screenshot_runner.py", "--url", target_url, "--mode", "compare"]
        return self._run_command("Visual Regression", command, phase_dir)

    def step_anomaly_detection(self) -> StepResult:
        phase_dir = self.root_dir / "phase3-ai" / "d-anomaly-detection"
        log_path = phase_dir / "sample_logs" / "app.log"
        if not self.dry_run and not log_path.exists():
            generate_result = self._run_command("Generate Sample Log", [sys.executable, "generate_sample_log.py"], phase_dir)
            if generate_result.status != "PASS":
                return StepResult(
                    name="Anomaly Detection",
                    status="FAIL",
                    duration_sec=generate_result.duration_sec,
                    output=generate_result.output,
                    error=generate_result.error,
                )
        command = [sys.executable, "anomaly_detector.py", "--log", str(log_path)]
        return self._run_command("Anomaly Detection", command, phase_dir)

    def step_generate_report(self, all_results: list[StepResult]) -> str:
        report_dir = self.phase4_dir / self.config.get("paths", {}).get("report_dir", "reports")
        dashboard_path = self.phase4_dir / "dashboard" / "index.html"
        report_dir.mkdir(parents=True, exist_ok=True)
        dashboard_path.parent.mkdir(parents=True, exist_ok=True)

        total = len(all_results)
        passed = sum(1 for result in all_results if result.status == "PASS")
        failed = sum(1 for result in all_results if result.status == "FAIL")
        skipped = sum(1 for result in all_results if result.status == "SKIP")

        rows = "\n".join(
            "<tr>"
            f"<td>{html.escape(result.name)}</td>"
            f"<td><span class=\"status {result.status.lower()}\">{html.escape(result.status)}</span></td>"
            f"<td>{result.duration_sec:.2f}s</td>"
            f"<td><pre>{html.escape(result.output or result.error)}</pre></td>"
            "</tr>"
            for result in all_results
        )

        content = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>AI-Assisted QA Pipeline Dashboard</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 32px; color: #1f2937; background: #f8fafc; }}
    .summary {{ display: flex; gap: 12px; margin: 16px 0; }}
    .card {{ background: #fff; border: 1px solid #ddd; border-radius: 8px; padding: 16px; min-width: 120px; }}
    .value {{ display: block; font-size: 28px; font-weight: 700; }}
    table {{ width: 100%; border-collapse: collapse; background: #fff; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; vertical-align: top; }}
    th {{ background: #f3f4f6; text-align: left; }}
    .status {{ color: #fff; border-radius: 999px; padding: 4px 10px; font-weight: 700; }}
    .pass {{ background: #16a34a; }}
    .fail {{ background: #dc2626; }}
    .skip {{ background: #6b7280; }}
    pre {{ white-space: pre-wrap; background: #111827; color: #f9fafb; padding: 10px; border-radius: 6px; }}
  </style>
</head>
<body>
  <h1>AI-Assisted QA Pipeline Dashboard</h1>
  <section>
    <h2>Summary</h2>
    <div class="summary">
      <div class="card">Total<span class="value">{total}</span></div>
      <div class="card">Pass<span class="value">{passed}</span></div>
      <div class="card">Fail<span class="value">{failed}</span></div>
      <div class="card">Skip<span class="value">{skipped}</span></div>
    </div>
  </section>
  <section>
    <h2>Step Results</h2>
    <table>
      <thead><tr><th>Step</th><th>Status</th><th>Duration</th><th>Output</th></tr></thead>
      <tbody>
        {rows}
      </tbody>
    </table>
  </section>
  <section>
    <h2>Cara Jalankan Manual</h2>
    <pre>python phase4-integration/pipeline.py --config phase4-integration/pipeline_config.yaml
python phase4-integration/pipeline.py --config phase4-integration/pipeline_config.yaml --dry-run</pre>
  </section>
  <section>
    <h2>Komponen ML</h2>
    <p>Fase 3A memakai rule-based generation dan prompt export. Fase 3B memakai SSIM untuk visual regression. Fase 3C memakai fallback strategy chain untuk self-healing locator. Fase 3D memakai Isolation Forest untuk anomaly detection dari log.</p>
  </section>
</body>
</html>
"""
        dashboard_path.write_text(content, encoding="utf-8")
        report_path = report_dir / "unified_dashboard.html"
        report_path.write_text(content, encoding="utf-8")
        return str(report_path)

    def run_all(self) -> list[StepResult]:
        steps = self.config.get("steps", {})
        results: list[StepResult] = []

        if steps.get("run_test_generation", False):
            results.append(self.step_generate_tests())
        else:
            results.append(StepResult("Generate Tests", "SKIP", 0.0, "", "disabled by config"))

        if steps.get("run_unit_tests", False):
            results.append(self.step_run_unit_tests())
        else:
            results.append(StepResult("Unit Tests", "SKIP", 0.0, "", "disabled by config"))

        if steps.get("run_visual", False):
            results.append(self.step_visual_regression())
        else:
            results.append(StepResult("Visual Regression", "SKIP", 0.0, "", "disabled by config"))

        if steps.get("run_anomaly", False):
            results.append(self.step_anomaly_detection())
        else:
            results.append(StepResult("Anomaly Detection", "SKIP", 0.0, "", "disabled by config"))

        report_path = self.step_generate_report(results)
        notify(results, report_path)
        return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Run AI-assisted QA pipeline")
    parser.add_argument("--config", default="pipeline_config.yaml", help="Path to pipeline config YAML")
    parser.add_argument("--dry-run", action="store_true", help="Print steps without executing commands")
    args = parser.parse_args()

    pipeline = QAPipeline(args.config)
    pipeline.dry_run = args.dry_run
    pipeline.run_all()


if __name__ == "__main__":
    main()
