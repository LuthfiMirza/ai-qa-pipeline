from __future__ import annotations

import pandas as pd


def extract_features(df: pd.DataFrame, window: str = "1min") -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(
            columns=[
                "window_start",
                "total_count",
                "error_count",
                "warning_count",
                "info_count",
                "error_rate",
                "unique_modules",
                "avg_response_time",
                "max_response_time",
                "time_since_last_error",
            ]
        )

    valid_df = df.dropna(subset=["timestamp"]).copy()
    valid_df["timestamp"] = pd.to_datetime(valid_df["timestamp"])
    valid_df = valid_df.set_index("timestamp").sort_index()

    grouped = valid_df.resample(window)
    features = pd.DataFrame(index=grouped.size().index)
    features["total_count"] = grouped.size()
    features["error_count"] = grouped.apply(lambda group: int((group["level"] == "ERROR").sum()))
    features["warning_count"] = grouped.apply(lambda group: int((group["level"] == "WARNING").sum()))
    features["info_count"] = grouped.apply(lambda group: int((group["level"] == "INFO").sum()))
    features["error_rate"] = (features["error_count"] / features["total_count"].replace(0, pd.NA)).fillna(0.0)
    features["unique_modules"] = grouped["module"].nunique().fillna(0)
    features["avg_response_time"] = grouped["response_time_ms"].mean().fillna(0.0)
    features["max_response_time"] = grouped["response_time_ms"].max().fillna(0.0)

    last_error_time = None
    time_since_last_error: list[float] = []
    error_timestamps = valid_df[valid_df["level"] == "ERROR"].index

    for window_start in features.index:
        current_errors = error_timestamps[(error_timestamps >= window_start) & (error_timestamps < window_start + pd.Timedelta(window))]
        if len(current_errors) > 0:
            last_error_time = current_errors.max()
            time_since_last_error.append(0.0)
        elif last_error_time is None:
            time_since_last_error.append(0.0)
        else:
            time_since_last_error.append(float((window_start - last_error_time).total_seconds()))

    features["time_since_last_error"] = time_since_last_error
    features = features.reset_index().rename(columns={"timestamp": "window_start"})
    return features.fillna(0)
