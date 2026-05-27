from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest

from feature_extractor import extract_features
from log_parser import get_summary, parse_log_file
from report_generator import generate_report

FEATURE_COLUMNS = [
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


class AnomalyDetector:
    def __init__(self, contamination: float = 0.05, n_estimators: int = 100, random_state: int = 42):
        self.model = IsolationForest(
            contamination=contamination,
            n_estimators=n_estimators,
            random_state=random_state,
        )
        self.feature_columns = FEATURE_COLUMNS
        self.is_trained = False

    def _feature_matrix(self, features_df: pd.DataFrame) -> pd.DataFrame:
        missing = [column for column in self.feature_columns if column not in features_df.columns]
        if missing:
            raise ValueError(f"Missing feature columns: {missing}")
        return features_df[self.feature_columns].fillna(0)

    def train(self, features_df: pd.DataFrame) -> "AnomalyDetector":
        if features_df.empty:
            raise ValueError("Cannot train anomaly detector with empty features")
        self.model.fit(self._feature_matrix(features_df))
        self.is_trained = True
        return self

    def predict(self, features_df: pd.DataFrame) -> pd.DataFrame:
        if not self.is_trained:
            raise ValueError("AnomalyDetector must be trained or loaded before predict()")

        predictions = features_df.copy()
        feature_matrix = self._feature_matrix(features_df)
        model_predictions = self.model.predict(feature_matrix)
        predictions["is_anomaly"] = model_predictions == -1
        predictions["anomaly_score"] = self.model.score_samples(feature_matrix)
        return predictions

    def save(self, path: str | Path) -> Path:
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
        return output_path

    @classmethod
    def load(cls, path: str | Path) -> "AnomalyDetector":
        payload: dict[str, Any] = joblib.load(path)
        detector = cls()
        detector.model = payload["model"]
        detector.feature_columns = payload.get("feature_columns", FEATURE_COLUMNS)
        detector.is_trained = payload.get("is_trained", True)
        return detector

    @staticmethod
    def get_anomaly_windows(df_with_predictions: pd.DataFrame) -> list[dict[str, Any]]:
        if df_with_predictions.empty or "is_anomaly" not in df_with_predictions.columns:
            return []
        return df_with_predictions[df_with_predictions["is_anomaly"]].to_dict(orient="records")


def run_pipeline(log_path: str | Path, window: str = "1min") -> tuple[pd.DataFrame, pd.DataFrame, Path]:
    logs_df = parse_log_file(log_path)
    summary = get_summary(logs_df)
    features_df = extract_features(logs_df, window=window)

    detector = AnomalyDetector()
    detector.train(features_df)
    predictions_df = detector.predict(features_df)
    detector.save("models/isolation_forest.pkl")
    report_path = generate_report(features_df, predictions_df, output_dir="reports")

    anomalies = detector.get_anomaly_windows(predictions_df)
    print(f"Parsed log rows: {summary['total']}")
    print(f"Errors: {summary['errors']} | Warnings: {summary['warnings']} | Error rate: {summary['error_rate']:.2%}")
    print(f"Feature windows: {len(features_df)}")
    print(f"Anomaly windows: {len(anomalies)}")
    print(f"Model saved: models/isolation_forest.pkl")
    print(f"Report saved: {report_path}")
    return features_df, predictions_df, report_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Detect anomalous log windows with Isolation Forest")
    parser.add_argument("--log", required=True, help="Path to application log file")
    parser.add_argument("--window", default="1min", help="Pandas resampling window, default: 1min")
    args = parser.parse_args()
    run_pipeline(args.log, window=args.window)


if __name__ == "__main__":
    main()
