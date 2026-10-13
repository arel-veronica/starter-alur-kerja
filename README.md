# 🚀 Starter Alur Kerja

Template proyek untuk membangun aplikasi bersama **Claude Code** dengan alur yang aman:
setiap perubahan datang sebagai **Pull Request**, kamu **uji dulu di server** dengan satu perintah,
baru di-**merge**. Kalau ada yang salah, server bisa kembali ke versi lama, dan data sudah di-backup otomatis.

Di dalamnya ada **bot Telegram contoh** (`/ping`, `/versi`) supaya kamu bisa mencoba seluruh alur dari awal
sampai akhir sebelum membangun proyekmu sendiri.

```
Kamu minta fitur ke Claude ─► Claude membuka PR ─► kamu uji di server ─► merge ─► server kembali ke main
```

👉 Penjelasan lengkap, gambar alur, dan "kalau X terjadi, lakukan Y" ada di **[ALUR-KERJA.md](ALUR-KERJA.md)**.

---

## Isi repo

| File / folder | Untuk apa |
|---|---|
| `rilis` | **Menu satu pintu** di server: status, uji PR, kembali ke main, log, backup |
| `scripts/pengaturan.sh` | ⚙️ Satu-satunya pengaturan skrip yang perlu diubah per proyek |
| `scripts/uji-pr`, `scripts/balik-main` | Mesin di balik menu `rilis` |
| `CLAUDE.md` | Aturan kerja yang otomatis dibaca Claude Code setiap sesi |
| `.github/pull_request_template.md` | Kerangka deskripsi PR (cara uji, dampak ke server) |
| `.github/workflows/tes.yml` | Tes otomatis di GitHub untuk setiap PR (✅/❌) |
| `app/`, `tests/` | Bot Telegram contoh + tesnya |
| `Dockerfile`, `docker-compose.yml` | Cara bot dijalankan di server |

---

## Mulai

### 1. Buat repo dari template
Klik **Use this template → Create a new repository** di GitHub. Beri nama proyekmu.

### 2. Aktifkan pengaman di GitHub (sekali saja)
Ikuti [ALUR-KERJA.md → Proteksi branch main](ALUR-KERJA.md#-proteksi-branch-main-sekali-saja).
Dengan ini GitHub sendiri yang menolak push langsung ke `main` dan merge selain *merge commit*.

### 3. Buat bot Telegram
1. Chat [@BotFather](https://t.me/BotFather) → `/newbot` → salin **token**-nya.
2. Simpan token itu; nanti diisi di `.env` di server.

### 4. Siapkan server (sekali saja)

Server butuh **Docker** (dengan `docker compose`) dan **git**. Ganti `NAMAREPO` dan `OWNER` di bawah.

**a. Buat kunci baca-saja (deploy key) khusus repo ini**
```bash
ssh-keygen -t ed25519 -f ~/.ssh/github-NAMAREPO -N "" -C "server NAMAREPO"
cat ~/.ssh/github-NAMAREPO.pub
```
Salin isinya ke GitHub: repo → **Settings → Deploy keys → Add deploy key**.
**Jangan** centang *Allow write access*: server cukup membaca.

**b. Daftarkan alias kunci itu** di `~/.ssh/config`:
```
Host github-NAMAREPO
  HostName github.com
  User git
  IdentityFile ~/.ssh/github-NAMAREPO
  IdentitiesOnly yes
```

**c. Clone dan isi pengaturan**
```bash
git clone git@github-NAMAREPO:OWNER/NAMAREPO.git && cd NAMAREPO
cp .env.example .env
nano .env                       # isi TELEGRAM_BOT_TOKEN, biarkan TELEGRAM_ALLOWED_CHAT_ID kosong dulu
mkdir -p data && sudo chown -R 1000:1000 data   # container berjalan sebagai user biasa (UID 1000)
```

### 5. Jalankan pertama kali
```bash
./rilis main
```
1. Kirim `/start` ke bot. Bot membalas dengan **chat ID**-mu.
2. Isi `TELEGRAM_ALLOWED_CHAT_ID` di `.env` dengan angka itu, lalu jalankan `./rilis main` lagi.
3. Sejak saat ini bot **hanya** melayani kamu. Coba `/ping` dan `/versi`.

### 6. Coba alurnya
Minta Claude Code membuat perubahan kecil, misalnya *"tambahkan perintah /halo yang membalas sapaan"*.
Lalu ikuti [ALUR-KERJA.md](ALUR-KERJA.md) dari langkah 2. Begitu `/halo` muncul di bot setelah merge,
kamu sudah menguasai seluruh alurnya 🎉

---

## Menyesuaikan untuk proyekmu sendiri

- [ ] `docker-compose.yml` → ganti `container_name: bot-contoh` dengan nama proyekmu
- [ ] `scripts/pengaturan.sh` → nama service (`SERVICE`) dan apa saja yang di-backup (`BACKUP_ITEMS`)
- [ ] `.env.example` → variabel yang dibutuhkan proyekmu (tanpa isi rahasia)
- [ ] `CLAUDE.md` → paragraf pertama: jelaskan proyekmu
- [ ] `app/` dan `tests/` → ganti dengan aplikasimu (atau minta Claude yang menggantinya, lewat PR)

Bukan Python atau bukan bot Telegram? Alurnya tetap sama. Yang perlu diubah hanya `Dockerfile`,
perintah tes di `.github/workflows/tes.yml`, dan baris "Sebelum membuka PR" di `CLAUDE.md`.

## Pengembangan di laptop (opsional)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pytest
```
