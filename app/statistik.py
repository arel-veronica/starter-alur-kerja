"""Contoh data yang disimpan bot: jumlah /ping.

Sengaja dibuat sederhana. Tujuannya menunjukkan bahwa bot punya *data* di folder data/
yang harus tetap aman saat kode diganti versi. Itulah alasan scripts/uji-pr membuat backup
data/ sebelum menjalankan PR.
"""

from __future__ import annotations

import json
from pathlib import Path

FILE_NAME = "statistik.json"


def _path(data_dir: Path) -> Path:
    return Path(data_dir) / FILE_NAME


def baca(data_dir: Path) -> dict:
    path = _path(data_dir)
    if not path.exists():
        return {"ping": 0}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"ping": 0}
    return data if isinstance(data, dict) else {"ping": 0}


def tambah_ping(data_dir: Path) -> int:
    """Naikkan hitungan /ping, simpan, lalu kembalikan nilai barunya."""
    data = baca(data_dir)
    data["ping"] = int(data.get("ping", 0)) + 1
    path = _path(data_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data), encoding="utf-8")
    tmp.replace(path)  # tulis-lalu-ganti: file tidak setengah jadi kalau bot mati di tengah jalan
    return data["ping"]
