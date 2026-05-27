from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", text.lower()).strip("_")
    return slug[:50] or "requirement"


def build_test_cases(requirement: str) -> list[dict[str, object]]:
    base_steps = [
        "Buka halaman atau fitur yang sesuai requirement",
        "Siapkan data uji yang dibutuhkan",
        "Jalankan aksi utama sesuai requirement",
    ]
    return [
        {
            "test_name": "test_login_valid_credentials",
            "description": f"Happy path untuk requirement: {requirement}",
            "category": "happy_path",
            "steps": [*base_steps, "Masukkan email dan password valid", "Klik tombol login"],
            "assertions": ["User berhasil login", "User diarahkan ke halaman dashboard atau area setelah login"],
        },
        {
            "test_name": "test_login_invalid_email",
            "description": "Sistem menolak login dengan email tidak valid",
            "category": "negative",
            "steps": [*base_steps, "Masukkan email tidak valid dan password valid", "Klik tombol login"],
            "assertions": ["Login gagal", "Pesan error email atau kredensial tampil"],
        },
        {
            "test_name": "test_login_invalid_password",
            "description": "Sistem menolak login dengan password salah",
            "category": "negative",
            "steps": [*base_steps, "Masukkan email valid dan password salah", "Klik tombol login"],
            "assertions": ["Login gagal", "Pesan error password atau kredensial tampil"],
        },
        {
            "test_name": "test_login_empty_fields",
            "description": "Sistem memvalidasi field login kosong",
            "category": "edge_case",
            "steps": [*base_steps, "Kosongkan email dan password", "Klik tombol login"],
            "assertions": ["Login gagal", "Validasi field wajib tampil"],
        },
    ]


def build_prompt(requirement: str, test_cases: list[dict[str, object]]) -> str:
    return (
        "Kamu adalah Senior QA Engineer.\n\n"
        "Buat test case dan kode Pytest/Playwright dari requirement berikut:\n\n"
        f"{requirement}\n\n"
        "Gunakan draft test case lokal ini sebagai baseline:\n\n"
        f"{json.dumps(test_cases, indent=2, ensure_ascii=False)}\n\n"
        "Output harus valid, executable, dan tidak memakai API berbayar."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Zero-API rule-based test generator with prompt export")
    parser.add_argument("--requirement", required=True, help="Requirement text")
    parser.add_argument("--export-prompt", action="store_true", help="Export ChatGPT-ready prompt")
    parser.add_argument("--json-only", action="store_true", help="Write JSON output only")
    parser.add_argument("--output-dir", default="examples/generated_tests", help="Output directory")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = slugify(args.requirement)
    test_cases = build_test_cases(args.requirement)

    json_path = output_dir / f"{slug}_{timestamp}.json"
    json_path.write_text(json.dumps(test_cases, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"JSON generated: {json_path}")

    if args.export_prompt:
        prompt_path = output_dir / f"{slug}_{timestamp}_prompt.md"
        prompt_path.write_text(build_prompt(args.requirement, test_cases), encoding="utf-8")
        print(f"Prompt exported: {prompt_path}")

    if not args.json_only:
        print(json.dumps(test_cases, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
