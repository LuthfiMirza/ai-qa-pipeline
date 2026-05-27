# AI-Assisted QA Pipeline

Sistem QA otomatis berbasis ML yang berjalan lokal tanpa API berbayar.

## Status Implementasi

- [x] Fase 1: Pytest unit test, Playwright UI test, coverage config
- [x] Fase 2: GitHub Actions CI, Page Object Model, parallel test
- [x] Fase 3A: Rule-based test generator + ChatGPT prompt export
- [x] Fase 3B: Visual regression dengan OpenCV + SSIM
- [x] Fase 3C: Self-healing locator dengan fallback strategy chain
- [x] Fase 3D: Anomaly detection dari log dengan Isolation Forest
- [x] Fase 4: Full integration pipeline + unified dashboard

## Quick Start

Setup virtual environment dari root project:

```bash
python -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
```

Install dependency utama untuk seluruh pipeline:

```bash
pip install -r phase4-integration/requirements.txt
playwright install chromium
```

Jalankan Fase 1 secara mandiri:

```bash
cd phase1-foundation
pytest
```

Jalankan Fase 2 secara mandiri:

```bash
cd phase2-automation
pytest -n auto
```

Jalankan Fase 3A secara mandiri:

```bash
cd phase3-ai/a-test-generation
python prompt_builder.py --input examples/input_requirements.txt --output examples/exported_prompt.md
python output_validator.py --input examples/generated_tests/login_test_cases.json
```

Jalankan Fase 3B secara mandiri:

```bash
cd phase3-ai/b-visual-regression
python screenshot_runner.py --url https://example.com --mode compare
```

Jalankan Fase 3C secara mandiri:

```bash
cd phase3-ai/c-self-healing
python healing_wrapper.py
```

Jalankan Fase 3D secara mandiri:

```bash
cd phase3-ai/d-anomaly-detection
python generate_sample_log.py
python anomaly_detector.py --log sample_logs/app.log
```

Jalankan Fase 4 secara mandiri:

```bash
cd phase4-integration
python pipeline.py --config pipeline_config.yaml
```

## Cara Jalankan Pipeline Penuh

```bash
python phase4-integration/pipeline.py --config phase4-integration/pipeline_config.yaml
```

Untuk melihat langkah tanpa menjalankan subprocess nyata:

```bash
python phase4-integration/pipeline.py --config phase4-integration/pipeline_config.yaml --dry-run
```

## Komponen ML

| Komponen | Teknik ML | Library | File Utama |
|---|---|---|---|
| Fase 3A: Test generation | Rule-based generation + human-in-the-loop LLM prompt export | Python standard library | `phase3-ai/a-test-generation/prompt_builder.py` |
| Fase 3B: Visual regression | Structural Similarity Index Measure atau SSIM | OpenCV, scikit-image, Pillow | `phase3-ai/b-visual-regression/visual_comparator.py` |
| Fase 3C: Self-healing locator | Fallback strategy chain + similarity matching | sentence-transformers, torch | `phase3-ai/c-self-healing/healing_wrapper.py` |
| Fase 3D: Log anomaly detection | Isolation Forest | scikit-learn, pandas, joblib | `phase3-ai/d-anomaly-detection/anomaly_detector.py` |

## Workflow AI Tanpa API

Pipeline ini tidak bergantung pada GPT API, Claude API, atau API berbayar lain. AI digunakan dengan pola human-in-the-loop agar tetap hemat biaya dan mudah dikontrol.

Alurnya:

```text
Requirement atau user story
        ↓
Rule-based generator membaca requirement
        ↓
Prompt export membuat prompt terstruktur
        ↓
Prompt di-copy ke ChatGPT Plus
        ↓
Hasil ChatGPT di-paste ke folder generated_tests
        ↓
Output divalidasi dengan validator lokal
        ↓
Test dijalankan dengan Pytest atau Playwright
```

Dengan pendekatan ini, project tetap bisa berjalan lokal, hasil AI tetap direview manusia, dan validasi akhir tetap dilakukan oleh automation test.
