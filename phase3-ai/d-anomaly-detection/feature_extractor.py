from __future__ import annotations

import pandas as pd

NUMERIC_COLUMNS = [
    "error_count",
    "warning_count",
    "info_count",
    "total_count",
    "error_rate",
    "unique_modules",
    "avg_response_time",
    "max_response_time",
    "time_since_last_error",
]


def extract_features(df: pd.DataFrame, window: str = "1min") -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["window_start", "window_end", *NUMERIC_COLUMNS])

    logs = df.dropna(subset=["timestamp"]).copy()
    logs["timestamp"] = pd.to_datetime(logs["timestamp"])
    logs = logs.set_index("timestamp").sort_index()

    grouped = logs.resample(window)
    features = pd.DataFrame(index=grouped.size().index)
    features["total_count"] = grouped.size()
    features["error_count"] = grouped.apply(lambda group: int((group["level"] == "ERROR").sum()))
    features["warning_count"] = grouped.apply(lambda group: int((group["level"] == "WARNING").sum()))
    features["info_count"] = grouped.apply(lambda group: int((group["level"] == "INFO").sum()))
    features["error_rate"] = features["error_count"] / features["total_count"].replace(0, pd.NA)
    features["unique_modules"] = grouped["module"].nunique()
    features["avg_response_time"] = grouped["response_time_ms"].mean()
    features["max_response_time"] = grouped["response_time_ms"].max()

    last_error_time = None
    time_since_last_error = []
    error_timestamps = logs[logs["level"] == "ERROR"].index
    window_delta = pd.Timedelta(window)

    for window_start in features.index:
        current_errors = error_timestamps[
            (error_timestamps >= window_start) & (error_timestamps < window_start + window_delta)
        ]
        if len(current_errors) > 0:
            last_error_time = current_errors.max()
            time_since_last_error.append(0.0)
        elif last_error_time is None:
            time_since_last_error.append(0.0)
        else:
            time_since_last_error.append(float((window_start - last_error_time).total_seconds()))

    features["time_since_last_error"] = time_since_last_error
    features = features.reset_index().rename(columns={"timestamp": "window_start"})
    features["window_end"] = features["window_start"] + window_delta
    features[NUMERIC_COLUMNS] = features[NUMERIC_COLUMNS].fillna(0)
    return features[["window_start", "window_end", *NUMERIC_COLUMNS]]
