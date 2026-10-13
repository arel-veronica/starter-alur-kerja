"""Pengaturan bot, dibaca dari environment variable (file .env)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:  # .env opsional saat jalan di laptop; di Docker sudah dibaca lewat env_file
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # pragma: no cover
    pass

BASE_DIR = Path(__file__).resolve().parent.parent


class ConfigError(RuntimeError):
    """Pengaturan wajib belum diisi atau formatnya salah."""


@dataclass(frozen=True)
class Settings:
    telegram_token: str
    allowed_chat_id: int | None  # None = bot belum dikunci ke pemiliknya
    data_dir: Path
    git_commit: str  # versi kode yang sedang berjalan (diisi skrip rilis saat build)
    git_branch: str


def load_settings(env: dict[str, str] | None = None) -> Settings:
    env = dict(os.environ if env is None else env)
    token = (env.get("TELEGRAM_BOT_TOKEN") or "").strip()
    if not token:
        raise ConfigError("TELEGRAM_BOT_TOKEN belum diisi di .env (ambil dari @BotFather).")

    raw_chat = (env.get("TELEGRAM_ALLOWED_CHAT_ID") or "").strip()
    try:
        allowed = int(raw_chat) if raw_chat else None
    except ValueError as exc:
        raise ConfigError(f"TELEGRAM_ALLOWED_CHAT_ID harus berupa angka, bukan {raw_chat!r}.") from exc

    data_dir = Path(env.get("DATA_DIR") or "data")
    if not data_dir.is_absolute():
        data_dir = BASE_DIR / data_dir

    return Settings(
        telegram_token=token,
        allowed_chat_id=allowed,
        data_dir=data_dir,
        git_commit=(env.get("GIT_COMMIT") or "dev").strip(),
        git_branch=(env.get("GIT_BRANCH") or "lokal").strip(),
    )
