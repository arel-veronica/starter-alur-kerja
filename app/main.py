"""Titik masuk bot: python -m app.main"""

from __future__ import annotations

import logging
import sys

from telegram import Update
from telegram.ext import Application

from .config import ConfigError, Settings, load_settings
from .handlers import DAFTAR_PERINTAH, register_handlers

log = logging.getLogger("bot")


async def _setelah_mulai(app: Application) -> None:
    await app.bot.set_my_commands(DAFTAR_PERINTAH)
    settings: Settings = app.bot_data["settings"]
    log.info("Bot siap · commit %s · branch %s", settings.git_commit, settings.git_branch)
    if settings.allowed_chat_id is None:
        log.warning("TELEGRAM_ALLOWED_CHAT_ID kosong: kirim /start ke bot untuk melihat chat ID-mu.")


def build_application(settings: Settings) -> Application:
    app = Application.builder().token(settings.telegram_token).post_init(_setelah_mulai).build()
    app.bot_data["settings"] = settings
    register_handlers(app)
    return app


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)  # jangan cetak URL berisi token bot ke log
    try:
        settings = load_settings()
    except ConfigError as exc:
        log.error("%s", exc)
        sys.exit(1)
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    build_application(settings).run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()
