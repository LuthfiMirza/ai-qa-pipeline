# Multi-Project Configs

Gunakan folder ini untuk menyimpan konfigurasi pipeline per project/client.

## Cara Membuat Config Baru

1. Copy `template.yaml` menjadi nama project baru, misalnya `client_baru.yaml`.
2. Isi `project_name`, `project_url`, `target_urls`, dan `requirements`.
3. Jalankan pipeline dengan config tersebut.

```bash
python pipeline.py --config configs/client_baru.yaml
```

Atau dari folder `phase4-integration`:

```bash
python pipeline.py --config ../configs/client_baru.yaml
```

Output report, baseline, dan log akan dipisahkan berdasarkan `project_name` agar beberapa client tidak saling overwrite.
