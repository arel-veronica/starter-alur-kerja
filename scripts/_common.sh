# shellcheck shell=bash
# Fungsi bersama untuk scripts/uji-pr, scripts/balik-main, dan ./rilis.
# File ini di-source, bukan dijalankan langsung. Pengaturan per proyek ada di scripts/pengaturan.sh.
#
# Prinsip:
# - Tidak pernah menjalankan `docker compose down -v`, menghapus volume, atau menghapus backup.
# - Tidak pernah mencetak isi .env. Output log disaring lewat `samarkan`.

# shellcheck source=scripts/pengaturan.sh
source "$(dirname "${BASH_SOURCE[0]}")/pengaturan.sh"

langkah() { printf '\n==> %s\n' "$*"; }
info() { printf '    %s\n' "$*"; }
gagal() {
  printf '\n✖ %s\n' "$*" >&2
  exit 1
}

# Saring pola kredensial yang mungkin muncul di log. Tambahkan pola untuk layanan lain bila perlu.
samarkan() {
  sed -u -E \
    -e 's#[0-9]{6,12}:[A-Za-z0-9_-]{30,}#<token-telegram-disamarkan>#g' \
    -e 's#sk-ant-[A-Za-z0-9_-]+#<kunci-anthropic-disamarkan>#g' \
    -e 's#sk-[A-Za-z0-9_-]{20,}#<kunci-api-disamarkan>#g' \
    -e 's#ya29\.[A-Za-z0-9._-]+#<token-google-disamarkan>#g' \
    -e 's#gh[pousr]_[A-Za-z0-9]{20,}#<token-github-disamarkan>#g'
}

# Cegah dua skrip berjalan bersamaan (mis. dari dua terminal).
kunci() {
  local lockfile
  lockfile="$(git rev-parse --absolute-git-dir)/alur-kerja.lock"
  exec 9>"$lockfile"
  flock -n 9 || gagal "Skrip lain (uji-pr/balik-main) sedang berjalan. Tunggu sampai selesai."
}

cek_prasyarat() {
  command -v git >/dev/null || gagal "git tidak ditemukan."
  command -v flock >/dev/null || gagal "flock tidak ditemukan (paket util-linux)."
  docker compose version >/dev/null 2>&1 || gagal "docker compose tidak tersedia."
  [[ -f .env ]] || gagal ".env belum ada. Buat dulu: cp .env.example .env, lalu isi."
}

cek_bersih() {
  if [[ -n "$(git status --porcelain)" ]]; then
    git status --short | sed 's/^/    /'
    gagal "Ada file yang berubah di server (lihat di atas). Server tidak boleh punya perubahan sendiri: semua perubahan lewat PR. Buang perubahan itu (git restore <file> / git clean -n untuk melihat file baru) lalu ulangi."
  fi
  info "Working tree bersih."
}

# Versi yang ditanam ke image, ditampilkan bot lewat /versi.
siapkan_versi() {
  GIT_COMMIT="$(git log -1 --format='%h')"
  GIT_BRANCH="$(git branch --show-current 2>/dev/null || echo detached)"
  export GIT_COMMIT GIT_BRANCH
}

tampilkan_aktif() {
  langkah "Versi yang aktif"
  info "Branch : $(git branch --show-current 2>/dev/null || true)"
  info "Commit : $(git log -1 --format='%h %s (%an, %cr)')"
  docker compose ps "$SERVICE" | sed 's/^/    /'
}

# Catat waktu sebelum `up`, supaya lihat_log hanya menampilkan log versi yang baru dinyalakan.
tandai_mulai() { MULAI="$(date -u +%Y-%m-%dT%H:%M:%SZ)"; }

lihat_log() {
  local detik="$1"
  langkah "Log ${detik} detik pertama (kredensial disamarkan)"
  # timeout keluar dengan kode 124; itu memang yang diharapkan.
  timeout "$detik" docker compose logs -f --no-color --since "${MULAI:?tandai_mulai belum dipanggil}" "$SERVICE" 2>&1 \
    | samarkan || true
}

# Salin BACKUP_ITEMS ke backups/<waktu>-<label>/. Tidak pernah menimpa backup lama.
# Argumen: <label> <keterangan>. Mencetak path folder backup ke variabel BACKUP_DIR.
backup_data() {
  local label="$1" ket="$2" ts i item
  ts="$(date +%Y%m%d-%H%M%S)"
  BACKUP_DIR="backups/${ts}-${label}"
  umask 077
  mkdir -p backups
  i=2
  while ! mkdir "$BACKUP_DIR" 2>/dev/null; do
    BACKUP_DIR="backups/${ts}-${label}-$i"
    i=$((i + 1))
  done
  for item in "${BACKUP_ITEMS[@]}"; do
    if [[ -e "$item" ]]; then
      mkdir -p "$BACKUP_DIR/$(dirname "$item")"
      cp -a "$item" "$BACKUP_DIR/$item"
    else
      info "$item belum ada — dilewati."
    fi
  done
  {
    echo "dibuat     : $(date -Iseconds)"
    echo "keterangan : $ket"
    echo "isi        : ${BACKUP_ITEMS[*]}"
  } >"$BACKUP_DIR/MANIFEST.txt"
  info "Tersimpan di $BACKUP_DIR ($(du -sh "$BACKUP_DIR" | cut -f1))"
}

# Daftar branch pr-<N> lokal (pernah diuji) yang commit-nya belum masuk origin/main.
# Karena merge selalu "Create a merge commit", commit PR yang sudah di-merge pasti menjadi leluhur
# main. Butuh: git fetch origin main sudah dijalankan.
pr_belum_merge() {
  local br
  while IFS= read -r br; do
    [[ "$br" =~ ^pr-[1-9][0-9]*$ ]] || continue
    git merge-base --is-ancestor "$br" origin/main || printf '%s\n' "$br"
  done < <(git for-each-ref --format='%(refname:short)' 'refs/heads/pr-*')
}

# Peringatan + konfirmasi sebelum kembali ke main bila ada PR yang diuji tapi belum di-merge.
# Status "terbuka" diambil dari ref refs/pull/<N>/merge di GitHub, yang hanya ada untuk PR terbuka
# yang bisa di-merge. Argumen: <branch-asal> <ya: 0|1>
cek_pr_belum_merge() {
  local asal="$1" ya="$2" br n status terbuka belum=()
  mapfile -t belum < <(pr_belum_merge)

  if [[ ${#belum[@]} -eq 0 ]]; then
    info "Tidak ada. Semua salinan pr-<N> yang pernah diuji sudah masuk main."
    return 0
  fi

  terbuka="$(git ls-remote origin 'refs/pull/*/merge' 2>/dev/null | sed -E 's#.*refs/pull/([0-9]+)/merge$#\1#' || true)"

  printf '\n⚠️  Ada PR yang pernah diuji di server tetapi BELUM di-merge ke main:\n'
  for br in "${belum[@]}"; do
    n="${br#pr-}"
    if grep -qx "$n" <<<"$terbuka"; then
      status="masih terbuka di GitHub"
    else
      status="status tidak diketahui: ditutup tanpa merge, sedang konflik, atau GitHub tidak terjangkau"
    fi
    if [[ "$br" == "$asal" ]]; then
      status="$status · SEDANG BERJALAN di server"
    fi
    printf '    • PR #%s (%s) — %s\n' "$n" "$(git log -1 --format='%h %s' "$br")" "$status"
  done
  printf '\n    Kembali ke main berarti fitur PR di atas hilang dari server sampai PR-nya di-merge.\n'
  printf '    Kalau sebuah PR sudah ditutup tanpa merge, hapus salinannya supaya peringatan ini hilang:\n'
  printf '        git branch -D pr-<N>\n\n'

  if [[ "$ya" == 1 ]]; then
    info "--ya diberikan: lanjut kembali ke main."
    return 0
  fi
  if [[ ! -t 0 ]]; then
    gagal "Tidak ada terminal untuk konfirmasi. Ulangi dengan: ./rilis main --ya"
  fi
  local jawab
  read -r -p "    Tetap kembali ke main? [y/N] " jawab
  case "$jawab" in
    y | Y | ya | Ya | YA) info "Lanjut kembali ke main." ;;
    *) gagal "Dibatalkan. Server tetap di ${asal:-(detached)}." ;;
  esac
}
