## Ringkasan
<!-- Apa yang berubah dan kenapa, dalam bahasa sederhana -->

## Cara menguji di server
```bash
./rilis uji <N>
```
Lalu di Telegram:
- [ ] `/versi` → menunjukkan `PR #<N>`
- [ ] ...

Selesai → `./rilis main`

## Dampak ke server
- Perubahan format data (`data/`): **tidak ada** / <jelaskan + apakah data lama tetap terbaca>
- Variabel `.env` baru: **tidak ada** / <sebutkan + nilai default>
- Perubahan `docker-compose.yml`: **tidak ada** / <jelaskan>

## Yang sudah dan belum diverifikasi
- Sudah: <mis. tes otomatis, dicoba dengan data tiruan>
- Belum: <mis. perilaku layanan sungguhan yang hanya bisa dilihat di server>

## Checklist
- [ ] Tes otomatis ✅ (lihat bagian bawah halaman PR)
- [ ] Tidak ada token/kata sandi/data pribadi yang tercetak ke log
- [ ] Merge dengan **Create a merge commit**
