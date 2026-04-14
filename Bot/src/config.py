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


def _normalize_signal_source(raw: str) -> str:
    v = (raw or "polymarket").strip().lower()
    if v in ("polymarket", "poly", "real", "live"):
        return "polymarket"
    if v in ("demo", "mock", "fake"):
        return "demo"
    logger.warning("Unknown SIGNAL_SOURCE=%r, using polymarket", raw)
    return "polymarket"


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
    log_level: str
    # Polymarket Data API (real signals)
    signal_source: str  # polymarket | demo
    polymarket_data_api_base: str
    polymarket_trades_limit: int
    polymarket_max_trade_age_sec: int


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
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        signal_source=_normalize_signal_source(os.getenv("SIGNAL_SOURCE", "polymarket")),
        polymarket_data_api_base=os.getenv(
            "POLYMARKET_DATA_API_BASE", "https://data-api.polymarket.com"
        ).rstrip("/"),
        polymarket_trades_limit=int(os.getenv("POLYMARKET_TRADES_LIMIT", "100")),
        polymarket_max_trade_age_sec=int(os.getenv("POLYMARKET_MAX_TRADE_AGE_SEC", "600")),
    )
