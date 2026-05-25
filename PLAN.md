# 📋 PLAN.md — Execution Plan AI-Assisted QA Pipeline

> Dokumen ini adalah panduan eksekusi lengkap. Ikuti urutan fase. Setiap fase punya checklist, kode starter, dan perintah yang bisa langsung dijalankan.

---

## FASE 1 — Fondasi QA (Minggu 1–4)

### 🎯 Tujuan
Menguasai konsep testing manual dan automation dasar sebelum masuk ML.

### ✅ Checklist Fase 1

**Minggu 1–2: Konsep & Pytest**
- [ ] Pahami konsep: test case, bug report, test coverage
- [ ] Setup project Python dengan virtual environment
- [ ] Tulis 5 unit test pakai Pytest untuk fungsi sederhana
- [ ] Jalankan test dan lihat output report
- [ ] Tambahkan coverage report (`pytest --cov`)

**Minggu 3–4: Playwright Web UI Testing**
- [ ] Install Playwright dan jalankan browser pertama
- [ ] Tulis test untuk buka website dan cek title
- [ ] Tulis test untuk klik tombol dan isi form
- [ ] Tangkap screenshot saat test gagal
- [ ] Buat minimal 10 test case UI untuk satu halaman web

### 📂 File yang akan dibuat
```
phase1-foundation/
├── requirements.txt
├── src/
│   └── calculator.py          ← contoh fungsi yang akan ditest
├── tests/
│   ├── test_calculator.py     ← unit test dengan Pytest
│   └── test_ui_login.py       ← UI test dengan Playwright
├── pytest.ini                 ← konfigurasi Pytest
└── README.md
```

### 💻 Perintah untuk AI Coding Agent
```
Buat struktur folder phase1-foundation/ dengan:
1. File src/calculator.py berisi fungsi add, subtract, multiply, divide
2. File tests/test_calculator.py dengan minimal 10 test case Pytest
   termasuk test untuk edge case (divide by zero, negative numbers)
3. File tests/test_ui_login.py dengan Playwright untuk test login page
   menggunakan https://practicetestautomation.com/practice-test-login/
4. File pytest.ini dengan konfigurasi html report dan coverage
5. File requirements.txt dengan semua dependensi
```

### 📖 Konsep Wajib Dipahami
- **Test Case**: skenario spesifik yang diuji (input → expected output)
- **Bug Report**: format laporan bug (steps to reproduce, expected, actual)
- **Test Coverage**: persentase kode yang tercakup test
- **Assertion**: pernyataan yang harus benar agar test pass
- **Fixtures**: data/setup yang dipakai berulang di berbagai test

---

## FASE 2 — Automation Pipeline (Minggu 5–8)

### 🎯 Tujuan
Membangun CI/CD pipeline agar test jalan otomatis tanpa trigger manual.

### ✅ Checklist Fase 2

**Minggu 5–6: GitHub Actions**
- [ ] Push project ke GitHub repository
- [ ] Buat `.github/workflows/test.yml`
- [ ] Test jalan otomatis setiap ada push ke main
- [ ] Tambahkan badge status test di README
- [ ] Setup test paralel untuk mempercepat eksekusi

**Minggu 7–8: Reporting & Maintenance**
- [ ] Install pytest-html untuk HTML report
- [ ] Setup Allure report (opsional, lebih lengkap)
- [ ] Buat test yang maintainable dengan Page Object Model
- [ ] Tambahkan retry logic untuk flaky test
- [ ] Konfigurasi notifikasi (email/Slack) saat test gagal

### 📂 File yang akan dibuat
```
phase2-automation/
├── .github/
│   └── workflows/
│       ├── test.yml           ← CI pipeline utama
│       └── schedule.yml       ← test terjadwal (cron)
├── tests/
│   ├── pages/
│   │   └── login_page.py      ← Page Object Model
│   └── test_e2e.py
├── reports/                   ← output HTML reports
├── conftest.py                ← Pytest fixtures global
└── README.md
```

### 💻 Perintah untuk AI Coding Agent
```
Buat struktur phase2-automation/ dengan:
1. .github/workflows/test.yml yang:
   - Trigger on push ke branch main dan pull request
   - Setup Python 3.11
   - Install dependencies dari requirements.txt
   - Jalankan pytest dengan html report
   - Upload report sebagai GitHub Actions artifact
2. conftest.py dengan fixture browser Playwright (session scope)
3. tests/pages/login_page.py dengan Page Object Model pattern
4. tests/test_e2e.py yang menggunakan page object tersebut
5. Tambahkan pytest-html dan pytest-xdist ke requirements.txt
```

### 📖 Konsep Wajib Dipahami
- **CI/CD**: Continuous Integration / Continuous Deployment
- **Page Object Model (POM)**: pattern untuk test yang maintainable
- **Fixtures**: setup dan teardown yang reusable
- **Flaky Test**: test yang kadang pass kadang fail tanpa alasan jelas
- **Parallelism**: jalankan test secara paralel untuk lebih cepat

---

## FASE 3A — AI-Assisted Test Case Generation Tanpa API (Minggu 9–10)

### 🎯 Tujuan
Membangun test case generator dengan pendekatan **zero-API human-in-the-loop**: sistem membaca requirement, membuat test case awal secara rule-based, lalu mengekspor prompt terstruktur yang bisa di-copy ke ChatGPT Plus atau LLM web lain tanpa memakai API key.

### 🧭 Prinsip Desain

- **No paid API required**: tidak wajib memakai Claude API, OpenAI API, atau API berbayar lain.
- **Default lokal**: rule-based generator tetap bisa berjalan offline.
- **Manual LLM workflow**: prompt diekspor ke file `.md`, lalu user copy-paste ke ChatGPT Plus.
- **Output tervalidasi**: hasil dari ChatGPT disimpan ulang ke project dan dicek agar valid JSON/Python/Pytest.
- **Extensible**: adapter untuk local LLM atau paid API boleh ditambahkan nanti, tapi bukan core requirement.

### 🔁 Workflow Fase 3A

```text
Requirement/User Story
        ↓
Rule-based parser membaca requirement
        ↓
Generate draft test cases lokal
        ↓
Build prompt terstruktur
        ↓
Export prompt ke examples/exported_prompt.md
        ↓
Copy prompt ke ChatGPT Plus
        ↓
Paste hasil AI ke generated_tests/
        ↓
Validate output dengan Pytest / JSON schema
```

### ✅ Checklist Fase 3A

- [ ] Buat input requirement dalam file teks
- [ ] Buat rule-based parser untuk membaca requirement/user story
- [ ] Generate draft test case lokal tanpa AI API
- [ ] Buat prompt builder yang menghasilkan prompt siap pakai untuk ChatGPT Plus
- [ ] Export prompt ke file Markdown agar mudah di-copy
- [ ] Siapkan format output yang diminta dari ChatGPT: JSON atau Python Pytest
- [ ] Buat folder `generated_tests/` untuk menyimpan hasil dari ChatGPT
- [ ] Buat validator sederhana untuk mengecek output JSON/Python
- [ ] Jalankan test yang dihasilkan dengan Pytest
- [ ] Dokumentasikan manual workflow copy-paste ChatGPT Plus

### 📂 File yang akan dibuat
```text
phase3-ai/a-test-generation/
├── requirements.txt
├── prompt_builder.py              ← membuat prompt siap copy ke ChatGPT Plus
├── rule_based_generator.py        ← generator lokal tanpa AI API
├── output_validator.py            ← validasi output JSON/Python/Pytest
├── prompt_templates/
│   ├── test_case_prompt.md        ← prompt untuk generate test case JSON
│   └── pytest_generation_prompt.md← prompt untuk generate kode Pytest
├── examples/
│   ├── input_requirements.txt     ← contoh requirement input
│   ├── exported_prompt.md         ← prompt hasil generate untuk di-copy
│   └── generated_tests/           ← hasil paste dari ChatGPT
└── README.md
```

### 💻 Perintah untuk AI Coding Agent / Codex
```text
Buat phase3-ai/a-test-generation/ dengan pendekatan zero-API:
1. prompt_builder.py yang:
   - Baca requirement dari argument CLI atau file
   - Baca template prompt dari prompt_templates/
   - Gabungkan requirement + instruksi output + konteks QA
   - Simpan prompt akhir ke examples/exported_prompt.md
   - Tidak memanggil API eksternal apa pun
2. rule_based_generator.py yang:
   - Parse requirement sederhana berbasis keyword/rule
   - Generate draft test case lokal dengan kategori happy_path, negative, edge_case
   - Output bisa berupa JSON agar mudah divalidasi
3. output_validator.py yang:
   - Validasi JSON test case dari hasil ChatGPT
   - Cek field wajib: test_name, description, category, steps, assertions
   - Untuk file Python, jalankan minimal compile check agar syntax valid
4. prompt_templates/test_case_prompt.md yang:
   - Meminta ChatGPT bertindak sebagai Senior QA Engineer
   - Meminta output JSON array yang strict
   - Meminta minimal happy path, negative test, dan edge case
5. prompt_templates/pytest_generation_prompt.md yang:
   - Meminta ChatGPT membuat kode Pytest valid
   - Meminta kode tanpa dependency berbayar/API
   - Meminta assertion yang jelas dan executable
6. README.md dengan workflow:
   - Jalankan prompt_builder.py
   - Copy isi exported_prompt.md
   - Paste ke ChatGPT Plus
   - Simpan hasil ke examples/generated_tests/
   - Jalankan validator dan Pytest
```

### 🧠 Contoh Prompt Export untuk ChatGPT Plus
```markdown
Kamu adalah Senior QA Engineer.

Tugasmu adalah membuat test case dari requirement berikut:

"User dapat login menggunakan email dan password yang valid. Jika email atau password salah, sistem menampilkan pesan error."

Output HARUS berupa JSON array valid tanpa markdown fence.
Setiap item harus punya field:
- test_name
- description
- category: happy_path | negative | edge_case
- steps
- assertions

Buat minimal:
- 3 happy path test
- 3 negative test
- 2 edge case test

Pastikan test case jelas, bisa dieksekusi manual, dan mudah dikonversi menjadi Pytest/Playwright.
```

### 🧪 Contoh Perintah Lokal
```bash
# Generate prompt dari requirement
python prompt_builder.py --input examples/input_requirements.txt --output examples/exported_prompt.md

# Setelah hasil ChatGPT disimpan sebagai JSON
python output_validator.py --input examples/generated_tests/login_test_cases.json

# Jika hasil ChatGPT berupa file Pytest
python -m py_compile examples/generated_tests/test_login_generated.py
pytest examples/generated_tests/test_login_generated.py
```

### 📖 Konsep Wajib Dipahami
- **Human-in-the-loop AI**: AI membantu proses, tapi manusia tetap melakukan copy-paste, review, dan validasi.
- **Prompt Export**: sistem membuat prompt siap pakai tanpa memanggil API.
- **Rule-based Generation**: generator lokal berbasis aturan sederhana sebagai fallback gratis.
- **Output Validation**: hasil AI tidak dipercaya mentah-mentah; harus dicek struktur dan syntax.
- **Zero-API Architecture**: project tidak bergantung pada secret key, billing, atau provider tertentu.

---

## FASE 3B — Visual Regression Testing (Minggu 11–12)

### 🎯 Tujuan
Gunakan Computer Vision untuk mendeteksi perubahan visual UI secara otomatis.

### ✅ Checklist Fase 3B

- [ ] Install OpenCV dan scikit-image
- [ ] Ambil screenshot baseline UI
- [ ] Implementasi perbandingan pixel-level (SSIM)
- [ ] Highlight area yang berbeda dengan bounding box
- [ ] Set threshold toleransi (berapa % perubahan dianggap gagal)
- [ ] Integrasikan dengan Playwright untuk screenshot otomatis
- [ ] Buat HTML report yang menampilkan before/after/diff

### 📂 File yang akan dibuat
```
phase3-ai/b-visual-regression/
├── requirements.txt           ← opencv-python, scikit-image, Pillow
├── visual_comparator.py       ← engine perbandingan gambar
├── screenshot_runner.py       ← ambil screenshot dengan Playwright
├── baselines/                 ← screenshot referensi (baseline)
├── current/                   ← screenshot terbaru
├── diffs/                     ← gambar hasil diff (merah = berubah)
├── reports/
│   └── visual_report.html     ← HTML report with images
└── README.md
```

### 💻 Perintah untuk AI Coding Agent
```
Buat phase3-ai/b-visual-regression/ dengan:
1. visual_comparator.py dengan fungsi:
   - compare_screenshots(baseline_path, current_path) → dict {ssim_score, diff_image, regions_changed}
   - highlight_differences(img1, img2) → annotated image dengan bounding box merah
   - is_regression(ssim_score, threshold=0.95) → bool
2. screenshot_runner.py yang:
   - Gunakan Playwright untuk screenshot halaman web
   - Simpan ke folder baselines/ (pertama kali) atau current/ (berikutnya)
   - Otomatis jalankan comparison setelah capture
3. report_generator.py yang buat HTML report dengan:
   - Tabel: URL | SSIM Score | Status | Link ke diff image
   - Tampilkan baseline, current, dan diff side-by-side
4. Contoh penggunaan: python screenshot_runner.py --url https://example.com --mode compare
```

### 🧠 Algoritma SSIM
```python
from skimage.metrics import structural_similarity as ssim
import cv2

def compare(img1_path, img2_path):
    img1 = cv2.imread(img1_path, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(img2_path, cv2.IMREAD_GRAYSCALE)
    score, diff = ssim(img1, img2, full=True)
    # score mendekati 1.0 = identik, mendekati 0 = sangat berbeda
    return score, diff
```

---

## FASE 3C — Self-Healing Test (Minggu 13–15)

### 🎯 Tujuan
Buat test yang bisa auto-repair saat elemen UI berubah lokasi/atribut.

### ✅ Checklist Fase 3C

- [ ] Pahami kenapa test sering gagal (locator strategy)
- [ ] Implementasi multi-strategy locator (ID → CSS → XPath → text → position)
- [ ] Train similarity model untuk mengenali elemen secara semantik
- [ ] Buat fallback chain: coba satu per satu sampai ketemu
- [ ] Simpan "memory" elemen yang berhasil ditemukan
- [ ] Auto-update locator di test file jika fallback berhasil
- [ ] Test dengan halaman yang sengaja diubah layout-nya

### 📂 File yang akan dibuat
```
phase3-ai/c-self-healing/
├── requirements.txt           ← sentence-transformers, playwright
├── element_finder.py          ← smart element locator
├── locator_memory.json        ← penyimpanan locator yang berhasil
├── similarity_engine.py       ← model untuk similarity matching
├── healing_wrapper.py         ← wrapper di atas Playwright
├── tests/
│   └── test_with_healing.py   ← contoh test pakai self-healing
└── README.md
```

### 💻 Perintah untuk AI Coding Agent
```
Buat phase3-ai/c-self-healing/ dengan:
1. element_finder.py dengan class SmartLocator yang:
   - Punya method find_element(page, strategies_dict) 
   - strategies_dict berisi berbagai cara menemukan elemen:
     {"id": "submit-btn", "css": ".btn-primary", "text": "Submit", "xpath": "//button[@type='submit']"}
   - Coba satu per satu sampai berhasil
   - Log strategi mana yang berhasil
2. locator_memory.py yang:
   - Simpan {element_name: {strategy: locator}} ke JSON file
   - Update otomatis kalau strategi sebelumnya gagal tapi yang lain berhasil
3. similarity_engine.py yang:
   - Gunakan sentence-transformers untuk embed deskripsi elemen
   - Cari elemen di halaman yang paling mirip secara semantik
   - Useful saat semua locator konvensional gagal
4. healing_wrapper.py yang wrap Playwright page object
   dengan auto-healing logic
```

---

## FASE 3D — Anomaly Detection dari Log (Minggu 16–17)

### 🎯 Tujuan
Deteksi bug dan anomali dari application log menggunakan unsupervised ML.

### ✅ Checklist Fase 3D

- [ ] Kumpulkan / generate sample application log
- [ ] Parse log menjadi format terstruktur (timestamp, level, message)
- [ ] Feature engineering dari log (frekuensi error, response time, dll)
- [ ] Train Isolation Forest untuk deteksi anomali
- [ ] Visualisasi hasil anomali
- [ ] Set alerting threshold
- [ ] Buat daily anomaly report

### 📂 File yang akan dibuat
```
phase3-ai/d-anomaly-detection/
├── requirements.txt           ← scikit-learn, pandas, matplotlib
├── log_parser.py              ← parse raw log jadi DataFrame
├── feature_extractor.py       ← feature engineering dari log
├── anomaly_detector.py        ← Isolation Forest model
├── visualizer.py              ← plot anomali timeline
├── sample_logs/
│   └── app.log                ← contoh log untuk testing
├── models/
│   └── isolation_forest.pkl   ← model tersimpan
└── README.md
```

### 💻 Perintah untuk AI Coding Agent
```
Buat phase3-ai/d-anomaly-detection/ dengan:
1. log_parser.py yang:
   - Parse log format: "2024-01-15 10:23:45 ERROR [auth] Login failed for user X"
   - Output: DataFrame dengan kolom timestamp, level, module, message
   - Handle berbagai format log (Apache, aplikasi custom, JSON log)
2. feature_extractor.py yang buat fitur:
   - error_rate_per_minute: jumlah ERROR dalam window 1 menit
   - response_time_ms: kalau ada di log
   - error_type_count: count per jenis error
   - time_since_last_error: detik sejak error terakhir
3. anomaly_detector.py dengan:
   - Train Isolation Forest: IsolationForest(contamination=0.05)
   - Simpan model ke models/isolation_forest.pkl
   - Fungsi predict(log_window) → {is_anomaly: bool, score: float, reason: str}
4. sample_logs/app.log dengan 1000+ baris log realistis termasuk beberapa anomali
5. Visualizer yang buat grafik timeline dengan anomali di-highlight merah
```

### 🧠 Kode Inti Anomaly Detection
```python
from sklearn.ensemble import IsolationForest
import pandas as pd

# Train
model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
model.fit(features_df)

# Predict: -1 = anomali, 1 = normal
predictions = model.predict(features_df)
scores = model.score_samples(features_df)  # makin negatif = makin anomali
```

---

## FASE 4 — Integrasi Full Pipeline (Minggu 18–19)

### 🎯 Tujuan
Gabungkan semua komponen jadi satu pipeline yang berjalan end-to-end.

### ✅ Checklist Fase 4

- [ ] Buat orchestrator script yang koordinasi semua komponen
- [ ] Buat unified config file (`pipeline_config.yaml`)
- [ ] Integrasikan ke GitHub Actions sebagai satu workflow
- [ ] Buat unified dashboard HTML untuk semua hasil
- [ ] Setup scheduling (jalan setiap hari/setiap jam)
- [ ] Tambahkan notifikasi Slack/email untuk critical failure
- [ ] Dokumentasikan cara run seluruh pipeline

### 📂 File yang akan dibuat
```
phase4-integration/
├── pipeline.py                ← orchestrator utama
├── pipeline_config.yaml       ← konfigurasi semua komponen
├── .github/workflows/
│   └── full_pipeline.yml      ← GitHub Actions full pipeline
├── dashboard/
│   └── index.html             ← unified report dashboard
├── notifier.py                ← Slack/email notification
└── README.md
```

### 💻 Perintah untuk AI Coding Agent
```
Buat phase4-integration/ dengan:
1. pipeline.py dengan class QAPipeline yang:
   - load_config(config_path) dari YAML
   - run_step_1_generate_tests(requirements_file)
   - run_step_2_execute_tests()  
   - run_step_3_visual_regression()
   - run_step_4_anomaly_detection(log_file)
   - run_step_5_generate_report()
   - run_all() yang jalankan semua step berurutan
   - Error handling: kalau satu step gagal, lanjut dan catat di report
2. pipeline_config.yaml dengan semua konfigurasi:
   - target_url, baseline_dir, log_dir, prompt_export_dir, thresholds, dll
3. .github/workflows/full_pipeline.yml yang:
   - Jalan setiap hari jam 08:00 WIB (cron: '0 1 * * *')
   - Dan setiap push ke main
   - Upload semua artifacts (report, screenshots, dll)
4. dashboard/index.html yang tampilkan semua hasil dalam satu halaman
   dengan status per komponen (✅ pass / ❌ fail / ⚠️ warning)
```

### 🏗️ Arsitektur Pipeline
```
[REQUIREMENT FILE]
       ↓
[3A: Rule-based draft + prompt export untuk ChatGPT Plus]
       ↓
[2: Jalankan test otomatis via Pytest/Playwright]
       ↓
[3B: Visual regression check screenshot]
       ↓
[3D: Anomaly detection dari application log]
       ↓
[4: Unified HTML report + notifikasi]
```

---

## 🔧 Urutan Eksekusi di AI Coding Agent

### Cara pakai dokumen ini:
Setiap "Perintah untuk AI Coding Agent" di atas bisa langsung kamu copy-paste ke Codex, Claude Code, atau coding assistant lain sebagai instruksi.

### Urutan yang disarankan:
```
1. Jalankan: "Buat phase1-foundation/ dengan..." → test dulu bisa jalan
2. Push ke GitHub, jalankan: "Buat phase2-automation/ dengan..."
3. Setelah CI/CD jalan, pilih salah satu dari 3A/3B/3C/3D
4. Mulai dari 3A (paling mudah dan langsung terasa manfaatnya)
5. Lanjut ke 3D (anomaly detection, murni ML klasik)
6. Terakhir baru 3B dan 3C (butuh lebih banyak setup)
7. Setelah semua jalan, integrasikan di Fase 4
```

---

## 📦 Dependencies Lengkap

### requirements-phase1.txt
```
pytest==8.0.0
pytest-html==4.1.1
pytest-cov==5.0.0
playwright==1.44.0
```

### requirements-phase2.txt
```
pytest-xdist==3.5.0     # parallel test
pytest-retry==0.6.2     # retry flaky test
allure-pytest==2.13.5   # advanced reporting
```

### requirements-phase3.txt
```
# 3A - AI-assisted prompt export tanpa API
# Tidak butuh dependency API berbayar. Gunakan standard library Python dulu.

# 3B - Visual CV
opencv-python==4.10.0.84
scikit-image==0.23.2
Pillow==10.3.0

# 3C - Self-healing
sentence-transformers==3.0.1
torch==2.3.0

# 3D - Anomaly Detection
scikit-learn==1.5.0
pandas==2.2.2
matplotlib==3.9.0
seaborn==0.13.2
```

---

## 💡 Tips Eksekusi

1. **Jangan loncat fase** — Fase 1 & 2 adalah fondasi. ML di atas automation yang rusak = percuma.
2. **Mulai dari 3A** — Paling cepat deliver value. Langsung bisa dipake tim.
3. **Dokumentasikan semua** — Tulis README per folder. Portfolio yang baik = dokumentasi yang baik.
4. **Commit sering** — Setiap fase selesai, buat git tag: `git tag v1.0-phase1`
5. **Ukur hasilnya** — Catat: berapa test yang jalan, berapa bug ditemukan, berapa waktu dihemat.

---

*Generated with AI-Assisted QA Pipeline Roadmap — zero-API, human-in-the-loop, siap eksekusi di AI coding agent*
