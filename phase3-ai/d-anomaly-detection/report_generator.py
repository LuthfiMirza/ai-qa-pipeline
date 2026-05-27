from __future__ import annotations

from datetime import datetime
from html import escape
from pathlib import Path

import pandas as pd

FEATURE_COLUMNS = [
    "error_count",
    "warning_count",
    "info_count",
    "error_rate",
    "unique_modules",
    "avg_response_time",
    "max_response_time",
    "time_since_last_error",
]


def _timeline_ascii(df_predictions: pd.DataFrame) -> str:
    if df_predictions.empty:
        return "No data"

    symbols = ["X" if row.is_anomaly else "." for row in df_predictions.itertuples()]
    chunks = []
    for index in range(0, len(symbols), 80):
        chunks.append("".join(symbols[index : index + 80]))
    return "\n".join(chunks)


def _format_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "<p>No anomalies detected.</p>"

    columns = ["window_start", "anomaly_score", *FEATURE_COLUMNS]
    available_columns = [column for column in columns if column in df.columns]
    rows = []
    for record in df[available_columns].to_dict(orient="records"):
        cells = "".join(f"<td>{escape(str(value))}</td>" for value in record.values())
        rows.append(f"<tr>{cells}</tr>")

    headers = "".join(f"<th>{escape(column)}</th>" for column in available_columns)
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table>"


def generate_report(df_features: pd.DataFrame, df_predictions: pd.DataFrame, output_dir: str | Path = "reports") -> Path:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = output_path / f"anomaly_report_{timestamp}.html"

    total_windows = len(df_predictions)
    anomaly_count = int(df_predictions["is_anomaly"].sum()) if total_windows else 0
    anomaly_rate = anomaly_count / total_windows if total_windows else 0.0
    anomaly_df = df_predictions[df_predictions["is_anomaly"]].copy() if total_windows else pd.DataFrame()

    avg_error_rate = float(df_features["error_rate"].mean()) if not df_features.empty else 0.0
    max_response_time = float(df_features["max_response_time"].max()) if not df_features.empty else 0.0

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Anomaly Detection Report</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 32px; color: #222; }}
    .cards {{ display: grid; grid-template-columns: repeat(4, minmax(140px, 1fr)); gap: 12px; }}
    .card {{ border: 1px solid #ddd; border-radius: 8px; padding: 16px; background: #fafafa; }}
    .value {{ font-size: 24px; font-weight: 700; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 16px; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; font-size: 13px; }}
    th {{ background: #f1f1f1; text-align: left; }}
    pre {{ background: #111; color: #eee; padding: 16px; overflow-x: auto; }}
    .legend {{ margin-top: 8px; color: #555; }}
  </style>
</head>
<body>
  <h1>Anomaly Detection Report</h1>
  <p>Generated at {escape(datetime.now().isoformat(timespec="seconds"))}</p>

  <h2>Summary</h2>
  <div class="cards">
    <div class="card"><div>Total Windows</div><div class="value">{total_windows}</div></div>
    <div class="card"><div>Anomalies</div><div class="value">{anomaly_count}</div></div>
    <div class="card"><div>Anomaly Rate</div><div class="value">{anomaly_rate:.2%}</div></div>
    <div class="card"><div>Avg Error Rate</div><div class="value">{avg_error_rate:.2%}</div></div>
  </div>
  <p><strong>Max response time:</strong> {max_response_time:.2f} ms</p>

  <h2>ASCII Timeline</h2>
  <pre>{escape(_timeline_ascii(df_predictions))}</pre>
  <div class="legend">Legend: <strong>.</strong> normal window, <strong>X</strong> anomalous window</div>

  <h2>Anomaly Windows</h2>
  {_format_table(anomaly_df)}
</body>
</html>
"""
    report_path.write_text(html, encoding="utf-8")
    return report_path
