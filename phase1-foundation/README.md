# Phase 1 — QA Foundation

Fase ini membangun fondasi QA automation dengan unit test Pytest dan UI test Playwright.

## Isi

- `src/calculator.py` — fungsi sederhana untuk latihan unit testing.
- `tests/test_calculator.py` — unit test dengan happy path dan edge cases.
- `tests/test_ui_login.py` — UI test login page memakai Playwright.
- `conftest.py` — screenshot otomatis saat UI test gagal.
- `pytest.ini` — konfigurasi report HTML dan coverage.

## Setup

```bash
cd phase1-foundation
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

## Jalankan Test

```bash
pytest tests/test_calculator.py
pytest tests/test_ui_login.py --browser chromium
pytest
```

## Output

- HTML test report: `reports/phase1-report.html`
- Coverage report: `reports/coverage/index.html`
- Screenshot gagal: `screenshots/`

## Catatan

UI test memakai website latihan publik `https://practicetestautomation.com/practice-test-login/`, jadi butuh koneksi internet saat dijalankan.
