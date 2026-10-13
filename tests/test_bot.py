"""Tes bot contoh. Jalankan dengan: pytest

Tes berjalan otomatis di GitHub setiap kali ada PR (lihat .github/workflows/tes.yml).
"""

import pytest

from app import statistik
from app.config import ConfigError, load_settings
from app.handlers import BANTUAN, DAFTAR_PERINTAH, boleh, sapaan, teks_versi


# --- pengaturan --------------------------------------------------------------
def test_pengaturan_minimal():
    s = load_settings({"TELEGRAM_BOT_TOKEN": "123:abc"})
    assert s.allowed_chat_id is None and s.git_commit == "dev" and s.git_branch == "lokal"


def test_pengaturan_lengkap(tmp_path):
    s = load_settings({
        "TELEGRAM_BOT_TOKEN": "123:abc", "TELEGRAM_ALLOWED_CHAT_ID": " 42 ",
        "DATA_DIR": str(tmp_path), "GIT_COMMIT": "a1b2c3d", "GIT_BRANCH": "pr-7",
    })
    assert s.allowed_chat_id == 42 and s.data_dir == tmp_path
    assert (s.git_commit, s.git_branch) == ("a1b2c3d", "pr-7")


def test_pengaturan_salah():
    with pytest.raises(ConfigError, match="TELEGRAM_BOT_TOKEN"):
        load_settings({})
    with pytest.raises(ConfigError, match="angka"):
        load_settings({"TELEGRAM_BOT_TOKEN": "x", "TELEGRAM_ALLOWED_CHAT_ID": "bukan-angka"})


# --- keamanan: hanya pemilik ---------------------------------------------------
def test_hanya_pemilik_yang_dilayani():
    assert boleh(42, 42)
    assert not boleh(99, 42)
    assert not boleh(42, None)  # bot belum dikunci → tidak melayani siapa pun (kecuali /start)
    assert not boleh(None, 42)


# --- data /ping ------------------------------------------------------------------
def test_ping_dihitung_dan_tersimpan(tmp_path):
    assert statistik.baca(tmp_path) == {"ping": 0}
    assert statistik.tambah_ping(tmp_path) == 1
    assert statistik.tambah_ping(tmp_path) == 2
    assert statistik.baca(tmp_path) == {"ping": 2}  # tetap ada setelah "restart"


def test_file_rusak_tidak_membuat_bot_mati(tmp_path):
    (tmp_path / statistik.FILE_NAME).write_text("{rusak")
    assert statistik.tambah_ping(tmp_path) == 1


# --- teks ----------------------------------------------------------------------------
def test_versi_menjelaskan_status():
    assert "menguji PR #7" in teks_versi("a1b2c3d", "pr-7")
    assert "produksi" in teks_versi("a1b2c3d", "main")
    assert "luar alur rilis" in teks_versi("dev", "lokal")
    assert "&lt;" in teks_versi("<x>", "main")  # karakter HTML aman


def test_semua_perintah_ada_di_bantuan():
    for cmd in DAFTAR_PERINTAH:
        assert f"/{cmd.command}" in BANTUAN


# --- /halo ---------------------------------------------------------------------------
@pytest.mark.parametrize("jam,waktu", [
    (4, "pagi"), (10, "pagi"), (11, "siang"), (14, "siang"),
    (15, "sore"), (17, "sore"), (18, "malam"), (23, "malam"), (0, "malam"), (3, "malam"),
])
def test_sapaan_sesuai_jam(jam, waktu):
    assert f"Selamat {waktu}, Arel!" in sapaan(jam, "Arel")


def test_sapaan_tanpa_nama_dan_nama_aman():
    assert sapaan(9, None).endswith("Selamat pagi!")
    assert sapaan(9, "  ").endswith("Selamat pagi!")
    assert "&lt;b&gt;" in sapaan(9, "<b>Arel</b>")  # nama tidak bisa menyisipkan HTML
