from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest

from feature_extractor import extract_features
from log_parser import get_summary, parse_log_file
from report_generator import generate_report

FEATURE_COLUMNS = [
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


class AnomalyDetector:
    def __init__(self, contamination: float = 0.05, n_estimators: int = 100, random_state: int = 42):
        self.model = IsolationForest(
            contamination=contamination,
            n_estimators=n_estimators,
            random_state=random_state,
        )
        self.feature_columns = FEATURE_COLUMNS
        self.is_trained = False

    def _matrix(self, features_df: pd.DataFrame) -> pd.DataFrame:
        missing = [column for column in self.feature_columns if column not in features_df.columns]
        if missing:
            raise ValueError(f"Missing feature columns: {missing}")
        return features_df[self.feature_columns].fillna(0)

    def train(self, features_df: pd.DataFrame) -> "AnomalyDetector":
        if features_df.empty:
            raise ValueError("Cannot train with empty feature DataFrame")
        self.model.fit(self._matrix(features_df))
        self.is_trained = True
        return self

    def predict(self, features_df: pd.DataFrame) -> pd.DataFrame:
        if not self.is_trained:
            raise ValueError("Model is not trained. Call train() or load() first.")
        result = features_df.copy()
        matrix = self._matrix(features_df)
        result["is_anomaly"] = self.model.predict(matrix) == -1
        result["anomaly_score"] = self.model.score_samples(matrix)
        return result

    def save(self, path: str) -> None:
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(
            {
                "model": self.model,
                "feature_columns": self.feature_columns,
                "is_trained": self.is_trained,
            },
            output_path,
        )

    @classmethod
    def load(cls, path: str) -> "AnomalyDetector":
        payload = joblib.load(path)
        detector = cls()
        detector.model = payload["model"]
        detector.feature_columns = payload.get("feature_columns", FEATURE_COLUMNS)
        detector.is_trained = payload.get("is_trained", True)
        return detector

    @staticmethod
    def get_anomaly_windows(df: pd.DataFrame) -> list[dict[str, Any]]:
        if df.empty or "is_anomaly" not in df.columns:
            return []
        anomalies = df[df["is_anomaly"]].copy()
        windows = []
        for row in anomalies.itertuples(index=False):
            windows.append(
                {
                    "window_start": getattr(row, "window_start"),
                    "window_end": getattr(row, "window_end"),
                    "score": float(getattr(row, "anomaly_score")),
                }
            )
        return windows


def run(log_path: str) -> str:
    logs_df = parse_log_file(log_path)
    summary = get_summary(logs_df)
    features_df = extract_features(logs_df)
    detector = AnomalyDetector().train(features_df)
    predictions_df = detector.predict(features_df)
    anomaly_windows = detector.get_anomaly_windows(predictions_df)

    detector.save("models/isolation_forest.pkl")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = generate_report(summary, anomaly_windows, f"reports/anomaly_report_{timestamp}.html")

    print(f"Total logs: {summary['total']}")
    print(f"Errors: {summary['errors']} | Warnings: {summary['warnings']} | Info: {summary['info']}")
    print(f"Error rate: {summary['error_rate']:.2%}")
    print(f"Feature windows: {len(features_df)}")
    print(f"Anomaly windows: {len(anomaly_windows)}")
    print(f"Report saved: {report_path}")
    return report_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Detect anomalous log windows with Isolation Forest")
    parser.add_argument("--log", required=True, help="Path to application log file")
    args = parser.parse_args()
    run(args.log)


if __name__ == "__main__":
    main()
