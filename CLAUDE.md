# CLAUDE.md — aturan kerja proyek ini

<!-- Ganti paragraf ini dengan deskripsi proyekmu. -->
Bot Telegram contoh (Python, python-telegram-bot), berjalan di server dengan Docker Compose.
Detail pemakaian: `README.md`. Alur rilis lengkap untuk manusia: `ALUR-KERJA.md`.

Pemilik repo ini mungkin **pengembang pemula**. Jelaskan dengan bahasa sederhana, tanpa istilah
yang tidak dijelaskan, dan selalu beri langkah uji yang bisa diikuti satu per satu.

## Alur kerja

**Setiap perubahan lewat Pull Request dan diuji di server sebelum merge.**

```
Claude Code: branch + PR → pemilik membaca PR → uji di server: ./rilis uji <N>
      → merge commit di GitHub → server: ./rilis main
```

### Aturan

1. **Jangan pernah push langsung ke `main`.** Selalu kerja di branch sendiri (`claude/<topik-singkat>`)
   dan buka PR ke `main`.
2. **Server mengambil PR berdasarkan nomornya** (`git fetch origin pull/<N>/head:pr-<N>`).
   `scripts/uji-pr <N>` sudah mengerjakan ini, plus backup dan restart.
3. **Server hanya membaca dari GitHub** lewat deploy key SSH read-only. Server tidak pernah push dan
   tidak pernah punya perubahan lokal.
4. **Satu instance saja.** Saat menguji PR, versi produksi dihentikan, PR dijalankan, lalu kembali ke
   `main`. Jangan pernah menjalankan dua instance dengan token yang sama. `container_name` di
   `docker-compose.yml` sengaja dibuat tetap sebagai pengaman.
5. **Merge selalu "Create a merge commit"**, bukan squash atau rebase. Pengaman `balik-main`
   bergantung pada ini untuk mendeteksi PR yang belum di-merge.

### Skrip server

| Perintah | Yang dilakukan |
|---|---|
| `./rilis` | Menu: status server, uji PR, kembali ke main, log, daftar backup |
| `./rilis uji <N>` / `scripts/uji-pr <N>` | Tolak bila ada perubahan lokal → ambil PR #N → build → stop versi berjalan → backup `BACKUP_ITEMS` → jalankan PR → log 15 detik |
| `./rilis main` / `scripts/balik-main [--ya]` | Tolak bila ada perubahan lokal → peringatan + konfirmasi bila ada `pr-<N>` yang belum masuk `main` → `main` terbaru → jalankan → log 10 detik |

Pengaturan per proyek (nama service, apa yang di-backup) hanya ada di `scripts/pengaturan.sh`.
Skrip tidak pernah menjalankan `docker compose down -v`, menghapus volume, atau menghapus backup.

## Panduan untuk Claude Code

- **Sebelum menulis kode**, tunjukkan rencana singkat per PR dan tanyakan hanya keputusan yang benar-benar
  perlu. Pecah pekerjaan besar menjadi beberapa PR kecil yang bisa diuji sendiri-sendiri.
- Sebelum membuka PR: `pip install -r requirements-dev.txt && pytest` harus lolos. Tes yang sama berjalan
  otomatis di GitHub (`.github/workflows/tes.yml`), termasuk `shellcheck` untuk skrip.
- Isi deskripsi PR mengikuti `.github/pull_request_template.md`. Wajib ada:
  - **cara menguji** setelah `./rilis uji <N>`, langkah demi langkah;
  - **perubahan format data** di `data/`: PR harus tetap bisa membaca data lama, atau menjelaskan
    langkah pemulihannya;
  - **variabel `.env` baru** beserta nilai default-nya, karena server harus menambahkannya sebelum menguji;
  - apa yang **sudah** dan **belum** diverifikasi, dipisah.
- Setelah membuka PR, laporkan: apa yang berubah, apa yang sudah/belum diverifikasi, cara menguji,
  dan bagian permintaan yang tidak diikuti beserta alasannya.
- Jangan pernah commit `.env`, `data/`, atau `backups/`. Jangan mencetak token atau data pribadi ke log.
- Perubahan pada skrip di `scripts/` atau `rilis` harus tetap lolos `shellcheck -x`.
- Tulis teks untuk pengguna (pesan bot, dokumentasi) dalam bahasa Indonesia.
