from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urljoin

import yaml

ROOT_DIR = Path(__file__).resolve().parents[1]
CONFIG_TEMPLATE = ROOT_DIR / "configs" / "template.yaml"
CONFIG_DIR = ROOT_DIR / "configs"
PHASE4_DIR = ROOT_DIR / "phase4-integration"
VISUAL_DIR = ROOT_DIR / "phase3-ai" / "b-visual-regression"


def ask_non_empty(prompt: str) -> str:
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Error: input tidak boleh kosong.")


def ask_yes_no(prompt: str) -> bool:
    while True:
        value = ask_non_empty(prompt).lower()
        if value in {"y", "yes"}:
            return True
        if value in {"n", "no"}:
            return False
        print("Error: jawab dengan y atau n.")


def normalize_project_name(value: str) -> str:
    value = value.strip().replace(" ", "-")
    value = re.sub(r"[^A-Za-z0-9-]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value.lower()


def ask_project_name() -> str:
    while True:
        raw_name = ask_non_empty("Project name (contoh: toko-online-pak-budi, tanpa spasi): ")
        project_name = normalize_project_name(raw_name)
        if project_name:
            return project_name
        print("Error: project_name harus berisi huruf, angka, atau tanda hubung.")


def ask_base_url() -> str:
    while True:
        base_url = ask_non_empty("Base URL (contoh: https://tokopakbudi.com): ").rstrip("/")
        if base_url.startswith(("http://", "https://")):
            return base_url
        print("Error: base_url harus dimulai dengan http:// atau https://.")


def ask_paths() -> list[str]:
    while True:
        raw_paths = ask_non_empty("Halaman yang mau dites, pisah koma (contoh: /login,/dashboard,/checkout): ")
        paths = [item.strip() for item in raw_paths.split(",") if item.strip()]
        if paths:
            return [path if path.startswith("/") else f"/{path}" for path in paths]
        print("Error: masukkan minimal satu halaman.")


def build_urls(base_url: str, paths: list[str]) -> list[str]:
    return [urljoin(f"{base_url}/", path.lstrip("/")) for path in paths]


def write_config(project_name: str, base_url: str, target_urls: list[str], log_path: str | None) -> Path:
    template = yaml.safe_load(CONFIG_TEMPLATE.read_text(encoding="utf-8"))
    template["project_name"] = project_name
    template["project_url"] = base_url
    template["target_urls"] = target_urls
    template["paths"] = {
        "baseline_dir": f"../phase3-ai/b-visual-regression/baselines/{project_name}",
        "log_dir": f"logs/{project_name}",
        "report_dir": f"reports/{project_name}",
    }
    template["requirements"] = [f"Test halaman {url}" for url in target_urls]
    if log_path:
        template["source_log_file"] = log_path

    config_path = CONFIG_DIR / f"{project_name}.yaml"
    config_path.write_text(yaml.safe_dump(template, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return config_path


def create_folders(project_name: str) -> tuple[Path, Path, Path]:
    report_dir = PHASE4_DIR / "reports" / project_name
    log_dir = PHASE4_DIR / "logs" / project_name
    baseline_dir = VISUAL_DIR / "baselines" / project_name
    for folder in [report_dir, log_dir, baseline_dir]:
        folder.mkdir(parents=True, exist_ok=True)
    return report_dir, log_dir, baseline_dir


def write_urls_file(project_name: str, urls: list[str]) -> Path:
    urls_path = VISUAL_DIR / f"urls_{project_name}.txt"
    urls_path.write_text("\n".join(urls) + "\n", encoding="utf-8")
    return urls_path


def capture_baseline(project_name: str, urls_path: Path, baseline_dir: Path) -> None:
    command = [
        sys.executable,
        "screenshot_runner.py",
        "--urls-file",
        str(urls_path),
        "--mode",
        "baseline",
        "--baseline-dir",
        str(baseline_dir),
        "--report-dir",
        str(PHASE4_DIR / "reports" / project_name),
    ]
    completed = subprocess.run(command, cwd=VISUAL_DIR, text=True, capture_output=True, check=False)
    if completed.stdout:
        print(completed.stdout.strip())
    if completed.returncode != 0:
        if completed.stderr:
            print(completed.stderr.strip())
        raise SystemExit("Error: baseline screenshot gagal dibuat.")


def main() -> None:
    project_name = ask_project_name()
    base_url = ask_base_url()
    paths = ask_paths()
    has_log_file = ask_yes_no("Ada log file yang mau dianalisa? (y/n): ")
    log_path = ask_non_empty("Log file path: ") if has_log_file else None

    target_urls = build_urls(base_url, paths)
    config_path = write_config(project_name, base_url, target_urls, log_path)
    report_dir, _, baseline_dir = create_folders(project_name)
    urls_path = write_urls_file(project_name, target_urls)

    take_baseline = ask_yes_no("Ambil baseline screenshot sekarang? (y/n): ")
    if take_baseline:
        capture_baseline(project_name, urls_path, baseline_dir)
    else:
        print("Baseline screenshot diskip. Jalankan manual nanti:")
        print(
            f"cd phase3-ai/b-visual-regression && python screenshot_runner.py "
            f"--urls-file urls_{project_name}.txt --mode baseline "
            f"--baseline-dir baselines/{project_name}"
        )

    print(f"\n✓ Project '{project_name}' siap.\n")
    print(f"Config   : configs/{project_name}.yaml")
    print(f"URLs     : phase3-ai/b-visual-regression/urls_{project_name}.txt")
    print(f"Baseline : phase3-ai/b-visual-regression/baselines/{project_name}/")
    print(f"Report   : phase4-integration/reports/{project_name}/")
    print("\nJalankan pipeline:")
    print(f"python pipeline.py --config configs/{project_name}.yaml")
    print("\nJalankan dry-run dulu:")
    print(f"python pipeline.py --config configs/{project_name}.yaml --dry-run")


if __name__ == "__main__":
    main()
