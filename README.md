[![CI](https://github.com/LuthfiMirza/ai-qa-pipeline/actions/workflows/full_pipeline.yml/badge.svg)](https://github.com/LuthfiMirza/ai-qa-pipeline/actions)

# AI-Assisted QA Pipeline

Sistem QA otomatis berbasis ML — berjalan lokal, tanpa API berbayar.

## Status

| Fase | Status | Isi |
|---|---|---|
| Fase 1 | [x] Done | Pytest unit test, Playwright UI test, config portable |
| Fase 2 | [x] Done | GitHub Actions CI, Page Object Model, parallel test |
| Fase 3A | [x] Done | Rule-based generator dan ChatGPT prompt export |
| Fase 3B | [x] Done | Visual regression dengan OpenCV dan SSIM |
| Fase 3C | [x] Done | Self-healing locator fallback strategy |
| Fase 3D | [x] Done | Log anomaly detection dengan Isolation Forest |
| Fase 4 | [x] Done | Full integration pipeline dan dashboard |

## Quick Start

```bash
python -m venv venv
source venv/bin/activate
pip install -r phase4-integration/requirements.txt
python pipeline.py --config configs/project_demo.yaml
```

## Cara Jalankan Per Fase

- Fase 1: test kalkulator dan UI starter. `cd phase1-foundation && python -m pytest tests/test_calculator.py -v`
- Fase 2: automation suite CI/POM. `cd phase2-automation && python -m pytest -n auto`
- Fase 3A: generate test case lokal. `cd phase3-ai/a-test-generation && python generator.py --requirement "User dapat login" --export-prompt --json-only`
- Fase 3B: bandingkan screenshot UI. `cd phase3-ai/b-visual-regression && python screenshot_runner.py --url https://example.com --mode compare`
- Fase 3C: jalankan self-healing locator. `cd phase3-ai/c-self-healing && python healing_wrapper.py`
- Fase 3D: deteksi anomali log. `cd phase3-ai/d-anomaly-detection && python anomaly_detector.py --log sample_logs/app.log`
- Fase 4: orchestrator penuh. `python pipeline.py --config configs/project_demo.yaml`

## Komponen ML

| Komponen | Teknik | Library Utama | File |
|---|---|---|---|
| Test generation | Rule-based + prompt export | Python stdlib | `phase3-ai/a-test-generation/generator.py` |
| Visual regression | SSIM image comparison | OpenCV, scikit-image | `phase3-ai/b-visual-regression/visual_comparator.py` |
| Self-healing locator | Fallback chain + similarity | sentence-transformers | `phase3-ai/c-self-healing/healing_wrapper.py` |
| Log anomaly detection | Isolation Forest | scikit-learn, pandas | `phase3-ai/d-anomaly-detection/anomaly_detector.py` |

## Hasil Pipeline Terakhir

- Unit Tests: 12 passed
- Test Generator: menghasilkan 4 test case dari 1 requirement
- Anomaly Detection: diuji dengan 2000 baris log, terdeteksi 17 anomali
- Visual Regression: belum aktif (`run_visual: false`)

## Workflow AI Tanpa API

Project ini memakai AI dengan pola human-in-the-loop: generator lokal membuat draft dan prompt, lalu ChatGPT Plus dipakai manual tanpa API key.

```text
Requirement → generator.py → prompt.txt → ChatGPT Plus → paste JSON → pytest
```
