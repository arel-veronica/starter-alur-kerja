"""Perintah Telegram.

Untuk menambah perintah baru:
1. tulis fungsi `async def cmd_namaperintah(update, context)` di bawah, beri @hanya_pemilik;
2. daftarkan di `register_handlers()` paling bawah;
3. tambahkan ke DAFTAR_PERINTAH supaya muncul di menu Telegram;
4. tulis tesnya di tests/.
"""

from __future__ import annotations

import logging
from datetime import datetime
from functools import wraps
from html import escape

from telegram import BotCommand, Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes

from . import statistik

log = logging.getLogger(__name__)

DAFTAR_PERINTAH = [
    BotCommand("halo", "Sapaan sesuai waktu"),
    BotCommand("ping", "Cek bot hidup"),
    BotCommand("versi", "Versi kode yang sedang berjalan"),
    BotCommand("help", "Bantuan"),
]

BANTUAN = (
    "🤖 <b>Bot contoh</b>\n\n"
    "/halo — sapaan sesuai waktu (pagi/siang/sore/malam)\n"
    "/ping — cek bot hidup (dan hitung berapa kali sudah di-ping)\n"
    "/versi — versi kode yang sedang berjalan di server\n"
    "/help — pesan ini"
)


def boleh(chat_id: int | None, allowed: int | None) -> bool:
    """Hanya chat pemilik yang dilayani."""
    return allowed is not None and chat_id == allowed


def hanya_pemilik(func):
    """Abaikan diam-diam pesan dari chat selain pemilik bot."""

    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat = update.effective_chat
        if not boleh(chat.id if chat else None, context.bot_data["settings"].allowed_chat_id):
            log.info("Mengabaikan pesan dari chat %s", chat.id if chat else "?")
            return None
        return await func(update, context)

    return wrapper


async def _balas(update: Update, text: str) -> None:
    await update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Satu-satunya perintah yang dilayani sebelum bot dikunci: untuk mengetahui chat ID."""
    settings = context.bot_data["settings"]
    chat = update.effective_chat
    if settings.allowed_chat_id is None:
        await _balas(
            update,
            "👋 Bot belum dikunci ke pemiliknya.\n"
            f"Chat ID kamu: <code>{chat.id}</code>\n\n"
            "Isi <code>TELEGRAM_ALLOWED_CHAT_ID</code> dengan angka itu di <code>.env</code>, lalu restart bot.",
        )
        return
    if boleh(chat.id, settings.allowed_chat_id):
        await _balas(update, BANTUAN)


@hanya_pemilik
async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _balas(update, BANTUAN)


@hanya_pemilik
async def cmd_ping(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    n = statistik.tambah_ping(context.bot_data["settings"].data_dir)
    await _balas(update, f"🏓 pong! (ping ke-{n})")


def sapaan(jam: int, nama: str | None) -> str:
    """Sapaan sesuai jam (0–23, waktu server). Nama boleh kosong."""
    if 4 <= jam <= 10:
        waktu, emoji = "pagi", "🌅"
    elif 11 <= jam <= 14:
        waktu, emoji = "siang", "☀️"
    elif 15 <= jam <= 17:
        waktu, emoji = "sore", "🌇"
    else:
        waktu, emoji = "malam", "🌙"
    kepada = f", {escape(nama.strip())}" if nama and nama.strip() else ""
    return f"{emoji} Selamat {waktu}{kepada}!"


@hanya_pemilik
async def cmd_halo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Jam mengikuti zona waktu container (TZ=Asia/Jakarta di docker-compose.yml).
    user = update.effective_user
    await _balas(update, sapaan(datetime.now().hour, user.first_name if user else None))


def teks_versi(commit: str, branch: str) -> str:
    if branch.startswith("pr-"):
        status = f"🧪 sedang <b>menguji PR #{escape(branch[3:])}</b>. Selesai menguji → <code>./rilis</code> → kembali ke main"
    elif branch == "main":
        status = "✅ versi produksi (main)"
    else:
        status = "💻 dijalankan di luar alur rilis (mis. di laptop)"
    return f"🏷 Commit <code>{escape(commit)}</code> · branch <code>{escape(branch)}</code>\n{status}"


@hanya_pemilik
async def cmd_versi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings = context.bot_data["settings"]
    await _balas(update, teks_versi(settings.git_commit, settings.git_branch))


def register_handlers(app: Application) -> None:
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("halo", cmd_halo))
    app.add_handler(CommandHandler("ping", cmd_ping))
    app.add_handler(CommandHandler("versi", cmd_versi))
