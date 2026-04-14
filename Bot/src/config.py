from dataclasses import dataclass
import json
import logging
import os
import urllib.error
import urllib.request
from pathlib import Path

from dotenv import load_dotenv

_BOT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_BOT_ROOT / ".env")
load_dotenv()

logger = logging.getLogger(__name__)


def _resolve_bot_username(token: str, env_username: str) -> str:
    cleaned = env_username.strip().lstrip("@")
    if cleaned:
        return cleaned
    url = f"https://api.telegram.org/bot{token}/getMe"
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            data = json.load(resp)
        if data.get("ok") and data.get("result", {}).get("username"):
            return str(data["result"]["username"])
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
        logger.warning("getMe failed; set BOT_USERNAME in .env for share links")
    return "whale_signals_bot"


@dataclass(frozen=True)
class Settings:
    bot_token: str
    bot_username: str
    whale_threshold_usd: int
    signal_poll_interval_sec: int
    demo_live_min_interval_sec: int
    log_level: str


def load_settings() -> Settings:
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise ValueError("BOT_TOKEN is required")

    env_username = os.getenv("BOT_USERNAME", "").strip()
    username = _resolve_bot_username(token, env_username)

    return Settings(
        bot_token=token,
        bot_username=username,
        whale_threshold_usd=int(os.getenv("WHALE_THRESHOLD_USD", "100000")),
        signal_poll_interval_sec=int(os.getenv("SIGNAL_POLL_INTERVAL_SEC", "30")),
        demo_live_min_interval_sec=int(os.getenv("DEMO_LIVE_MIN_INTERVAL_SEC", "3600")),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )
