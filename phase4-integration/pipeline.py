from __future__ import annotations

import argparse
import html
import json
import re
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
        self.project_name = self._slugify_project_name(self.config.get("project_name", "default_project"))
        self.config["project_name"] = self.project_name
        self.dry_run = False
        self.project_paths = self._resolve_project_paths()
        for project_path in self.project_paths.values():
            project_path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _load_config(config_path: Path) -> dict:
        with config_path.open("r", encoding="utf-8") as file:
            return yaml.safe_load(file) or {}

    @staticmethod
    def _slugify_project_name(project_name: str) -> str:
        return re.sub(r"[^a-zA-Z0-9_-]+", "_", project_name.strip()).strip("_") or "default_project"

    def _format_project_path(self, value: str) -> Path:
        formatted = value.format(project_name=self.project_name)
        raw_path = Path(formatted)
        if raw_path.is_absolute():
            return raw_path
        return (self.phase4_dir / raw_path).resolve()

    def _resolve_project_paths(self) -> dict[str, Path]:
        paths = self.config.get("paths", {})
        return {
            "baseline_dir": self._format_project_path(paths.get("baseline_dir", "baselines/{project_name}")),
            "log_dir": self._format_project_path(paths.get("log_dir", "logs/{project_name}")),
            "report_dir": self._format_project_path(paths.get("report_dir", "reports/{project_name}")),
        }

    def _run_command(self, name: str, command: list[str], cwd: Path) -> StepResult:
        started = time.perf_counter()
        command_text = " ".join(command)

        if self.dry_run:
            print(f"DRY-RUN [{self.project_name}] {name}: cd {cwd} && {command_text}")
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
        requirements = self.config.get("requirements") or [self.config.get("sample_requirement", "User dapat login dengan email dan password")]
        requirement = requirements[0]
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
        urls_file = self.project_paths["baseline_dir"] / "urls.txt"
        urls_file.write_text("\n".join(self.config.get("target_urls", [])) + "\n", encoding="utf-8")
        command = [
            sys.executable,
            "../phase3-ai/b-visual-regression/screenshot_runner.py",
            "--urls-file",
            str(urls_file),
            "--mode",
            "compare",
            "--baseline-dir",
            str(self.project_paths["baseline_dir"]),
            "--current-dir",
            str(self.project_paths["baseline_dir"] / "current"),
            "--diff-dir",
            str(self.project_paths["baseline_dir"] / "diffs"),
            "--report-dir",
            str(self.project_paths["report_dir"]),
        ]
        return self._run_command("Visual Regression", command, self.phase4_dir)


    def step_self_healing_test(self) -> StepResult:
        phase_dir = self.root_dir / "phase3-ai" / "c-self-healing"
        started = time.perf_counter()
        command = [sys.executable, "run_healing_test.py"]
        command_text = " ".join(command)

        if self.dry_run:
            print(f"DRY-RUN [{self.project_name}] Self-Healing Test: cd {phase_dir} && {command_text}")
            return StepResult("Self-Healing Test", "SKIP", 0.0, command_text, "dry-run")

        if not phase_dir.exists():
            return StepResult("Self-Healing Test", "FAIL", 0.0, "", f"Missing directory: {phase_dir}")

        completed = subprocess.run(command, cwd=phase_dir, text=True, capture_output=True, check=False)
        duration = time.perf_counter() - started
        try:
            payload = json.loads(completed.stdout.strip().splitlines()[-1])
            status = payload.get("status", "PASS" if completed.returncode == 0 else "FAIL")
            output = (
                f"passed={payload.get('passed', 0)}, "
                f"failed={payload.get('failed', 0)}, "
                f"heal_count={payload.get('heal_count', 0)}"
            )
        except (IndexError, json.JSONDecodeError):
            status = "PASS" if completed.returncode == 0 else "FAIL"
            output = completed.stdout[-4000:]

        return StepResult(
            name="Self-Healing Test",
            status=status,
            duration_sec=duration,
            output=output,
            error=completed.stderr[-4000:],
        )

    def step_anomaly_detection(self) -> StepResult:
        phase_dir = self.root_dir / "phase3-ai" / "d-anomaly-detection"
        log_path = self.project_paths["log_dir"] / "app.log"
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
            generated_log = phase_dir / "sample_logs" / "app.log"
            if generated_log.exists():
                log_path.write_text(generated_log.read_text(encoding="utf-8"), encoding="utf-8")
        command = [sys.executable, "anomaly_detector.py", "--log", str(log_path)]
        return self._run_command("Anomaly Detection", command, phase_dir)

    def step_generate_report(self, all_results: list[StepResult]) -> str:
        report_dir = self.project_paths["report_dir"]
        report_dir.mkdir(parents=True, exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        run_date = time.strftime("%Y-%m-%d %H:%M:%S")
        report_path = report_dir / f"report_{timestamp}.html"
        latest_path = report_dir / "unified_dashboard.html"

        total = len(all_results)
        passed = sum(1 for result in all_results if result.status == "PASS")
        failed = sum(1 for result in all_results if result.status == "FAIL")
        duration_total = sum(result.duration_sec for result in all_results)
        overall_status = "PASS" if failed == 0 else "FAIL"

        issues = []
        for result in all_results:
            combined = f"{result.output}\n{result.error}".lower()
            if result.status == "FAIL":
                issues.append(f"{result.name}: {result.error or result.output or 'Step failed'}")
            elif "anomaly windows: 0" not in combined and "anomaly windows:" in combined:
                issues.append(f"{result.name}: anomaly windows detected")
            elif "visual regression" in result.name.lower() and "fail" in combined:
                issues.append(f"{result.name}: visual regression detected")

        if failed > 0 and any("visual" in issue.lower() for issue in issues):
            recommendation = "Visual changes detected. Review before deployment."
        elif any("anomaly" in issue.lower() for issue in issues):
            recommendation = "Anomaly patterns found in logs. Investigate server errors."
        elif failed == 0:
            recommendation = "All checks passed. Application is stable."
        else:
            recommendation = "Review failed checks before deployment."

        rows = "\n".join(
            "<tr>"
            f"<td>{html.escape(result.name)}</td>"
            f"<td><span class=\"status {result.status.lower()}\">{html.escape(result.status)}</span></td>"
            f"<td>{result.duration_sec:.2f}s</td>"
            f"<td><pre>{html.escape(result.output or result.error)}</pre></td>"
            "</tr>"
            for result in all_results
        )
        issues_html = "<p>No issues found</p>" if not issues else "<ul>" + "".join(
            f"<li>{html.escape(issue)}</li>" for issue in issues
        ) + "</ul>"

        content = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>QA Report — {html.escape(self.project_name)}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 32px; color: #1f2937; background: #f8fafc; }}
    header, section, footer {{ background: #fff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 20px; margin-bottom: 18px; }}
    h1, h2 {{ margin-top: 0; color: #111827; }}
    .overall {{ display: inline-block; color: #fff; border-radius: 999px; padding: 6px 14px; font-weight: 700; }}
    .overall.pass, .status.pass {{ background: #16a34a; }}
    .overall.fail, .status.fail {{ background: #dc2626; }}
    .status.skip {{ background: #6b7280; }}
    .summary {{ display: grid; grid-template-columns: repeat(4, minmax(120px, 1fr)); gap: 12px; }}
    .box {{ background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 10px; padding: 16px; }}
    .value {{ display: block; font-size: 28px; font-weight: 700; margin-top: 6px; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ border: 1px solid #e5e7eb; padding: 10px; text-align: left; vertical-align: top; }}
    th {{ background: #f3f4f6; }}
    .status {{ color: #fff; border-radius: 999px; padding: 4px 10px; font-weight: 700; }}
    pre {{ white-space: pre-wrap; max-height: 260px; overflow: auto; background: #111827; color: #f9fafb; padding: 12px; border-radius: 8px; }}
  </style>
</head>
<body>
  <header>
    <h1>QA Report — {html.escape(self.project_name)}</h1>
    <p>Run date: {html.escape(run_date)}</p>
    <p>Overall status: <span class="overall {overall_status.lower()}">{overall_status}</span></p>
  </header>

  <section>
    <h2>Summary</h2>
    <div class="summary">
      <div class="box">Total Steps<span class="value">{total}</span></div>
      <div class="box">Passed<span class="value">{passed}</span></div>
      <div class="box">Failed<span class="value">{failed}</span></div>
      <div class="box">Duration<span class="value">{duration_total:.1f}s</span></div>
    </div>
  </section>

  <section>
    <h2>Step Details</h2>
    <table>
      <thead><tr><th>Step</th><th>Status</th><th>Duration</th><th>Output</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
  </section>

  <section>
    <h2>Issues Found</h2>
    {issues_html}
  </section>

  <section>
    <h2>Recommendations</h2>
    <p>{html.escape(recommendation)}</p>
  </section>

  <footer>
    Generated by AI-Assisted QA Pipeline — {html.escape(run_date)}
  </footer>
</body>
</html>
"""
        report_path.write_text(content, encoding="utf-8")
        latest_path.write_text(content, encoding="utf-8")
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

        if steps.get("run_self_healing", False):
            results.append(self.step_self_healing_test())
        else:
            results.append(StepResult("Self-Healing Test", "SKIP", 0.0, "", "disabled by config"))

        if steps.get("run_anomaly", False):
            results.append(self.step_anomaly_detection())
        else:
            results.append(StepResult("Anomaly Detection", "SKIP", 0.0, "", "disabled by config"))

        report_path = self.step_generate_report(results)
        notify(results, report_path)
        return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Run AI-assisted QA pipeline")
    parser.add_argument("--config", default="configs/project_demo.yaml", help="Path to pipeline config YAML")
    parser.add_argument("--dry-run", action="store_true", help="Print steps without executing commands")
    args = parser.parse_args()

    pipeline = QAPipeline(args.config)
    pipeline.dry_run = args.dry_run
    pipeline.run_all()


if __name__ == "__main__":
    main()
