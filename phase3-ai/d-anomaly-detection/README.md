# Phase 3D — Log Anomaly Detection

Modul ini mendeteksi anomali dari application log menggunakan Isolation Forest.

## Workflow

```text
Raw application log
        ↓
log_parser.py
        ↓
feature_extractor.py
        ↓
anomaly_detector.py
        ↓
HTML report + saved model
```

## Setup

```bash
cd phase3-ai/d-anomaly-detection
pip install -r requirements.txt
```

## Generate Sample Log

```bash
python generate_sample_log.py
```

Output default: `sample_logs/app.log`.

## Run End-to-End

```bash
python anomaly_detector.py --log sample_logs/app.log
```

Output:

- Model: `models/isolation_forest.pkl`
- Report: `reports/anomaly_report_TIMESTAMP.html`

## Modul

- `log_parser.py` — parse log menjadi DataFrame dan summary.
- `feature_extractor.py` — agregasi fitur per window 1 menit.
- `anomaly_detector.py` — training, prediction, save/load model, dan CLI.
- `report_generator.py` — HTML report dengan summary, anomaly table, dan ASCII timeline.
