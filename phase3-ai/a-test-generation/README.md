# Phase 3A — Zero API Test Generator

Modul ini membuat draft test case dari requirement menggunakan rule-based generator lokal, lalu dapat mengekspor prompt terstruktur untuk dipakai manual di ChatGPT Plus. Modul ini tidak memanggil API berbayar, sehingga cocok untuk workflow AI-assisted dengan budget nol rupiah.

## Prerequisites

- Python 3.11+
- Tidak butuh API key
- Tidak butuh OpenAI API, Claude API, atau layanan LLM berbayar lain

## Cara Install

```bash
cd phase3-ai/a-test-generation
pip install -r requirements.txt
```

## Cara Pakai

Generate dari teks langsung:

```bash
python generator.py --requirement "User dapat login dengan email dan password" --json-only
```

Generate dari file:

```bash
python generator.py --requirement-file examples/input_requirements.txt --json-only
```

Generate test case dan export prompt untuk ChatGPT:

```bash
python generator.py --requirement "User dapat login dengan email dan password" --export-prompt --json-only
```

## Workflow AI Tanpa API

1. Requirement dibaca oleh generator lokal.
2. Generator membuat draft test case berbasis aturan sederhana.
3. Jika `--export-prompt` dipakai, prompt siap copy dibuat untuk ChatGPT Plus.
4. Hasil ChatGPT bisa ditempel kembali ke folder `examples/generated_tests/`.
5. Output akhir divalidasi dan dijalankan dengan Pytest atau Playwright.

## Contoh Output

```json
[
  {
    "test_name": "test_login_valid_credentials",
    "description": "User berhasil login dengan email dan password valid",
    "category": "happy_path",
    "steps": [
      "Buka halaman login",
      "Masukkan email valid",
      "Masukkan password valid",
      "Klik tombol login"
    ],
    "assertions": [
      "User berhasil masuk",
      "Dashboard atau halaman setelah login ditampilkan"
    ]
  }
]
```

## Struktur Folder Output

```text
examples/generated_tests/
├── example_output.json              # contoh output manual
├── requirement_slug_TIMESTAMP.json  # hasil test case dari generator
└── requirement_slug_TIMESTAMP_prompt.md # prompt untuk ChatGPT jika --export-prompt dipakai
```

## Import Hasil ChatGPT

Workflow import hasil ChatGPT:

1. Jalankan generator dengan `--export-prompt` untuk membuat prompt siap copy.
2. Paste prompt ke ChatGPT Plus dan minta output JSON sesuai format yang diminta.
3. Simpan hasil JSON ke file, misalnya `examples/chatgpt_output_example.json`.
4. Jalankan importer untuk mengubah JSON menjadi skeleton Pytest.

```bash
python importer.py --file examples/chatgpt_output_example.json --output examples/generated_tests/
```

Importer juga bisa membaca JSON langsung dari stdin:

```bash
cat examples/chatgpt_output_example.json | python importer.py --stdin
```

File Pytest yang dihasilkan memakai marker `@pytest.mark.generated`, berisi docstring langkah dan expected result, serta placeholder `pass` agar langsung bisa dijalankan tanpa error sebelum implementasi detail diisi.
