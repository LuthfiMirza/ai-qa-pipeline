from __future__ import annotations

from html import escape
from pathlib import Path


def _timeline(anomaly_windows: list[dict[str, object]], width: int = 80) -> str:
    if not anomaly_windows:
        return "|" + "." * width + "|"

    anomaly_count = min(len(anomaly_windows), width)
    chars = ["."] * width
    for index in range(anomaly_count):
        position = int(index * width / anomaly_count)
        chars[position] = "X"
    return "|" + "".join(chars) + "|"


def _anomaly_table(anomaly_windows: list[dict[str, object]]) -> str:
    if not anomaly_windows:
        return "<p>No anomaly windows detected.</p>"

    rows = []
    for item in anomaly_windows:
        rows.append(
            "<tr>"
            f"<td>{escape(str(item.get('window_start', '')))}</td>"
            f"<td>{escape(str(item.get('window_end', '')))}</td>"
            f"<td>{float(item.get('score', 0.0)):.6f}</td>"
            "</tr>"
        )
    return "<table><thead><tr><th>Window Start</th><th>Window End</th><th>Score</th></tr></thead><tbody>" + "".join(rows) + "</tbody></table>"


def generate_report(summary: dict[str, object], anomaly_windows: list[dict[str, object]], output_path: str) -> str:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Log Anomaly Detection Report</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 32px; color: #222; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 16px; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
    th {{ background: #f5f5f5; }}
    pre {{ background: #111; color: #eee; padding: 16px; overflow-x: auto; }}
  </style>
</head>
<body>
  <h1>Log Anomaly Detection Report</h1>
  <h2>Summary</h2>
  <p>Total logs: {summary.get('total', 0)}</p>
  <p>Errors: {summary.get('errors', 0)}</p>
  <p>Warnings: {summary.get('warnings', 0)}</p>
  <p>Info: {summary.get('info', 0)}</p>
  <p>Error rate: {float(summary.get('error_rate', 0.0)):.2%}</p>
  <p>Time range: {escape(str(summary.get('time_range', 'N/A')))}</p>
  <h2>ASCII Timeline</h2>
  <pre>{escape(_timeline(anomaly_windows))}</pre>
  <p>Legend: | = boundary, X = anomaly, . = normal window</p>
  <h2>Anomaly Windows</h2>
  {_anomaly_table(anomaly_windows)}
</body>
</html>
"""
    path.write_text(html, encoding="utf-8")
    return str(path)
