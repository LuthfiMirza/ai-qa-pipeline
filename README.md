[![CI](https://github.com/LuthfiMirza/ai-qa-pipeline/actions/workflows/full_pipeline.yml/badge.svg)](https://github.com/LuthfiMirza/ai-qa-pipeline/actions)

# AI-Assisted QA Pipeline

Pipeline QA otomatis berbasis ML yang bisa langsung dipakai untuk project freelance maupun tim kecil — berjalan 100% lokal, tanpa API berbayar.

Sekali setup, kamu bisa menjalankan QA lengkap untuk project manapun dalam satu perintah dan mengirim laporan HTML langsung ke client.

---

## Apa yang Dilakukan Pipeline Ini

Ketika kamu menjalankan pipeline, urutan ini berjalan otomatis:
Requirement teks
↓
[1] Generate test case dari requirement
↓
[2] Jalankan unit test otomatis
↓
[3] Cek visual UI — screenshot dibandingkan dengan baseline
↓
[4] Self-healing locator — test tetap jalan walau elemen UI berubah
↓
[5] Deteksi anomali dari application log
↓
[6] Laporan HTML siap dikirim ke client

Semua langkah ini berjalan dengan satu perintah:

```bash
python pipeline.py --config configs/nama-project.yaml
```

---

## Instalasi

**Prasyarat:** Python 3.11+, Git

```bash
# 1. Clone repo
git clone https://github.com/LuthfiMirza/ai-qa-pipeline.git
cd ai-qa-pipeline

# 2. Buat virtual environment
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

# 3. Install dependensi
pip install -r phase4-integration/requirements.txt

# 4. Install Playwright browser (untuk UI test dan screenshot)
playwright install chromium

# 5. Verifikasi instalasi
python pipeline.py --config configs/project_demo.yaml --dry-run
```

Output dry-run yang benar:
DRY-RUN [project_demo] Generate Tests
DRY-RUN [project_demo] Unit Tests
DRY-RUN [project_demo] Visual Regression
DRY-RUN [project_demo] Self-Healing Test
DRY-RUN [project_demo] Anomaly Detection

---

## Cara Pakai untuk Project Freelance

### Langkah 1 — Setup project client baru

```bash
python scripts/new_project.py
```

Script akan tanya interaktif:
Project name  : toko-online-pak-budi
Base URL      : https://tokopakbudi.com
Halaman dites : /login,/dashboard,/checkout
Ada log file? : n
Ambil baseline screenshot sekarang? : y

Setelah selesai, semua folder dan config terbuat otomatis.

### Langkah 2 — Jalankan QA

```bash
python pipeline.py --config configs/toko-online-pak-budi.yaml
```

Output yang akan muncul:
Generate Tests     PASS   0.3s
Unit Tests         PASS   1.2s
Visual Regression  PASS   4.1s
Self-Healing Test  PASS   2.3s
Anomaly Detection  PASS   1.8s
─────────────────────────────
TOTAL: 5 PASS, 0 FAIL, 0 SKIP
Report ready: phase4-integration/reports/toko-online-pak-budi/report_20260527_212521.html
File size  : 42 KB
Share via  : attach to email or upload to Google Drive

### Langkah 3 — Kirim laporan ke client

Buka file HTML yang disebutkan di output, lalu attach ke email atau upload ke Google Drive.

Laporan berisi:
- Status keseluruhan (PASS / FAIL)
- Detail tiap step
- Daftar isu yang ditemukan
- Rekomendasi otomatis

Setiap client punya folder terpisah — baseline, log, dan report tidak pernah saling overwrite.

---

## Komponen ML

| Komponen | Teknik | Library | Cara Kerja Singkat |
|---|---|---|---|
| Test generation | Rule-based + prompt export | Python stdlib | Baca requirement, generate test case, export prompt untuk ChatGPT |
| Visual regression | SSIM image comparison | OpenCV, scikit-image | Bandingkan screenshot piksel per piksel, highlight area yang berubah |
| Self-healing locator | Fallback chain | Playwright | Kalau selector berubah, coba strategi lain secara otomatis |
| Log anomaly detection | Isolation Forest | scikit-learn, pandas | Deteksi pola aneh di log yang mungkin jadi bug |

---

## Workflow AI Tanpa API Key

Pipeline ini tidak butuh API berbayar. AI dipakai secara manual dengan pola berikut:
Requirement
↓
generator.py membuat draft test case + prompt terstruktur
↓
Prompt di-copy ke ChatGPT Plus (manual, pakai akun sendiri)
↓
Hasil JSON dari ChatGPT di-paste ke folder generated_tests/
↓
importer.py konversi JSON jadi file Pytest yang valid
↓
Pipeline jalankan test otomatis

Kalau sudah punya API key di kemudian hari, tinggal ganti generator.py 
untuk hit API langsung tanpa ubah bagian pipeline lainnya.

---

## Hasil Pipeline Terakhir

| Step | Status | Detail |
|---|---|---|
| Generate Tests | PASS | 4 test case dari 1 requirement |
| Unit Tests | PASS | 12 test passed |
| Visual Regression | PASS | SSIM check aktif |
| Self-Healing Test | PASS | 2 test, 1 heal event |
| Anomaly Detection | PASS | 2000 baris log, 17 anomali terdeteksi |

---

## Struktur Project
ai-qa-pipeline/
├── pipeline.py                     ← entry point utama
├── configs/                        ← satu file per project/client
│   ├── template.yaml               ← template untuk client baru
│   └── project_demo.yaml           ← config demo
├── scripts/
│   └── new_project.py              ← setup otomatis project baru
├── phase1-foundation/              ← Pytest unit test dasar
├── phase2-automation/              ← CI/CD dan Page Object Model
├── phase3-ai/
│   ├── a-test-generation/          ← generator test case
│   ├── b-visual-regression/        ← screenshot comparison
│   ├── c-self-healing/             ← self-healing locator
│   └── d-anomaly-detection/        ← log anomaly detection
└── phase4-integration/             ← orchestrator dan report

---

## CI/CD

Pipeline jalan otomatis di GitHub Actions setiap:
- Push ke branch `main`
- Pull request ke `main`  
- Setiap hari jam 08.00 WIB (via cron schedule)

Lihat hasil run terakhir di tab [Actions](https://github.com/LuthfiMirza/ai-qa-pipeline/actions).

---

## Lisensi

MIT — bebas dipakai untuk project komersial maupun personal.
