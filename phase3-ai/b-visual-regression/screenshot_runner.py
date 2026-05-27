from __future__ import annotations

import argparse
import os
import re
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

from visual_comparator import compare_screenshots, is_regression


def slugify_url(url: str) -> str:
    parsed = urlparse(url)
    raw = f"{parsed.netloc}{parsed.path}".strip("/") or "page"
    return re.sub(r"[^a-zA-Z0-9]+", "_", raw).strip("_")


def read_urls(urls_file: str | None, url: str | None) -> list[str]:
    urls = []
    if urls_file:
        urls.extend(line.strip() for line in Path(urls_file).read_text(encoding="utf-8").splitlines() if line.strip())
    if url:
        urls.append(url)
    if not urls:
        raise ValueError("Provide --urls-file or --url")
    return urls


def capture(urls: list[str], mode: str, threshold: float, baseline_dir: str = "baselines", current_dir: str = "current", diff_dir: str = "diffs") -> list[dict[str, object]]:
    baseline_root = Path(baseline_dir)
    current_root = Path(current_dir)
    diff_root = Path(diff_dir)
    baseline_root.mkdir(parents=True, exist_ok=True)
    current_root.mkdir(parents=True, exist_ok=True)
    diff_root.mkdir(parents=True, exist_ok=True)
    results = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1366, "height": 768}, device_scale_factor=1)
        for url in urls:
            slug = slugify_url(url)
            baseline_path = baseline_root / f"{slug}.png"
            current_path = current_root / f"{slug}.png"
            diff_path = diff_root / f"{slug}_diff.png"

            page.goto(url, wait_until="networkidle", timeout=60000)
            page.screenshot(path=str(baseline_path if mode == "baseline" else current_path), full_page=True)

            if mode == "baseline":
                results.append({"url": url, "status": "BASELINE", "ssim_score": 1.0, "path": str(baseline_path)})
                continue

            if not baseline_path.exists():
                baseline_path.write_bytes(current_path.read_bytes())
                results.append({"url": url, "status": "BASELINE_CREATED", "ssim_score": 1.0, "path": str(baseline_path)})
                continue

            comparison = compare_screenshots(baseline_path, current_path, diff_path)
            regression = is_regression(comparison["ssim_score"], threshold=threshold)
            results.append({"url": url, "status": "FAIL" if regression else "PASS", **comparison})
        browser.close()
    return results


def write_report(results: list[dict[str, object]], report_dir: str = "reports") -> Path:
    Path(report_dir).mkdir(parents=True, exist_ok=True)
    rows = "\n".join(
        f"<tr><td>{item['url']}</td><td>{item['status']}</td><td>{float(item.get('ssim_score', 0)):.4f}</td><td>{item.get('diff_image', item.get('path', ''))}</td></tr>"
        for item in results
    )
    report = Path(report_dir) / "visual_report.html"
    report.write_text(
        "<!doctype html><html><head><meta charset='utf-8'><title>Visual Regression Report</title>"
        "<style>body{font-family:Arial;margin:32px}table{border-collapse:collapse;width:100%}td,th{border:1px solid #ddd;padding:8px}th{background:#f3f4f6}</style>"
        f"</head><body><h1>Visual Regression Report</h1><table><thead><tr><th>URL</th><th>Status</th><th>SSIM</th><th>Artifact</th></tr></thead><tbody>{rows}</tbody></table></body></html>",
        encoding="utf-8",
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Capture and compare website screenshots")
    parser.add_argument("--urls-file", help="Text file with one URL per line")
    parser.add_argument("--url", help="Single URL to capture")
    parser.add_argument("--mode", choices=["baseline", "compare"], required=True)
    parser.add_argument("--threshold", type=float, default=0.95)
    parser.add_argument("--baseline-dir", default="baselines")
    parser.add_argument("--current-dir", default="current")
    parser.add_argument("--diff-dir", default="diffs")
    parser.add_argument("--report-dir", default="reports")
    args = parser.parse_args()

    urls_file = str(Path(args.urls_file).resolve()) if args.urls_file else None
    os.chdir(Path(__file__).resolve().parent)
    urls = read_urls(urls_file, args.url)
    results = capture(
        urls,
        args.mode,
        args.threshold,
        baseline_dir=args.baseline_dir,
        current_dir=args.current_dir,
        diff_dir=args.diff_dir,
    )
    report = write_report(results, report_dir=args.report_dir)
    for item in results:
        print(f"{item['status']} {item['url']} SSIM={float(item.get('ssim_score', 0)):.4f}")
    print(f"Report saved: {report}")
    if any(item["status"] == "FAIL" for item in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
