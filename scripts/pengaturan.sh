# shellcheck shell=bash
# ⚙️  PENGATURAN PER PROYEK — satu-satunya file di scripts/ yang perlu diubah untuk proyek baru.
# File ini di-source oleh skrip lain, bukan dijalankan langsung.

# Nama service di docker-compose.yml yang dijalankan sebagai aplikasi.
# shellcheck disable=SC2034  # dipakai oleh _common.sh
SERVICE="bot"

# Folder/file data yang di-backup sebelum menguji PR (relatif terhadap folder repo).
# Isi dengan semua yang TIDAK ada di git tapi penting: database, konfigurasi pribadi, dsb.
# Contoh untuk proyek lain: BACKUP_ITEMS=(data config/rules.json)
# shellcheck disable=SC2034
BACKUP_ITEMS=(data)
