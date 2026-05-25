# 🤖 AI-Assisted QA Pipeline

Roadmap lengkap membangun sistem QA berbasis AI/ML dari nol — dari testing manual sampai pipeline QA modern berbasis automation, ML lokal, dan workflow human-in-the-loop tanpa wajib memakai API berbayar.

Project ini memakai pendekatan **zero-API hybrid**:

- Default berjalan lokal dengan rule-based generator, Pytest, Playwright, OpenCV, dan scikit-learn.
- AI/LLM digunakan secara manual lewat prompt export: tool membuat prompt, lalu prompt bisa di-copy ke ChatGPT Plus atau LLM web lain.
- Local LLM bisa ditambahkan nanti jika tersedia.
- Paid API bersifat opsional, bukan kebutuhan utama.

---

## 📁 Struktur Project

```
ai-assisted-qa-pipeline/
├── README.md                  ← kamu di sini
├── PLAN.md                    ← execution plan detail per fase
├── phase1-foundation/         ← Fase 1: QA Manual & Pytest dasar
├── phase2-automation/         ← Fase 2: CI/CD pipeline
├── phase3-ai/
│   ├── a-test-generation/     ← Prompt export + rule-based test generator
│   ├── b-visual-regression/   ← CV screenshot comparison
│   ├── c-self-healing/        ← Self-healing test dengan ML
│   └── d-anomaly-detection/   ← Log anomaly detection
└── phase4-integration/        ← Full pipeline terintegrasi
```

---

## 🗺️ Overview Roadmap

| Fase | Durasi | Isi | ML? |
|------|--------|-----|-----|
| 1 — Fondasi QA | 2–4 minggu | Test case, bug report, Pytest, Playwright | ❌ |
| 2 — Automation | 2–4 minggu | CI/CD, GitHub Actions, test reporting | ❌ |
| 3A — AI-Assisted Test Gen | 1–2 minggu | Rule-based generator + prompt export untuk ChatGPT Plus | ✅ Human-in-the-loop AI |
| 3B — Visual CV | 1–2 minggu | Screenshot comparison dengan OpenCV/CLIP | ✅ Computer Vision |
| 3C — Self-healing | 2–3 minggu | Auto-repair test saat UI berubah | ✅ Similarity ML |
| 3D — Anomaly | 1–2 minggu | Deteksi bug dari log pakai Isolation Forest | ✅ Unsupervised ML |
| 4 — Integrasi | 1–2 minggu | Full pipeline end-to-end | ✅ Semua |

---

## 🚀 Quick Start

```bash
# Clone / buat project baru
mkdir ai-assisted-qa-pipeline && cd ai-assisted-qa-pipeline

# Setup Python environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependensi dasar (Fase 1)
pip install pytest playwright requests

# Install Playwright browsers
playwright install chromium
```

---

## ✅ Status Implementasi

- [x] Dokumentasi roadmap awal (`README.md`, `PLAN.md`)
- [x] Fase 1 foundation: Pytest unit test, Playwright UI test starter, coverage config, HTML report config
- [ ] Fase 2 automation pipeline
- [ ] Fase 3A AI-assisted prompt export tanpa API
- [ ] Fase 3B/3C/3D ML-based QA modules
- [ ] Fase 4 full integration

---

## 🧠 Workflow AI Tanpa API

```text
Requirement/User Story
        ↓
Rule-based parser membaca requirement
        ↓
Tool membuat prompt terstruktur
        ↓
Copy prompt ke ChatGPT Plus
        ↓
Paste hasil AI ke folder generated_tests/
        ↓
Jalankan Pytest/Playwright untuk validasi
```

Dengan cara ini project tetap bisa berjalan dengan budget API `0 rupiah`, tapi masih memanfaatkan AI secara praktis melalui ChatGPT Plus yang dipakai manual.

---

## 📚 Baca selanjutnya

→ **[PLAN.md](./PLAN.md)** — Execution plan lengkap per fase, per minggu, per task
