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


def _parse_admin_user_ids(raw: str) -> tuple[int, ...]:
    values: list[int] = []
    for part in (raw or "").split(","):
        p = part.strip()
        if not p:
            continue
        try:
            values.append(int(p))
        except ValueError:
            logger.warning("Invalid ADMIN_USER_IDS value ignored: %r", p)
    return tuple(sorted(set(values)))


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
    whale_threshold_crypto_usd: int
    signal_poll_interval_sec: int
    alert_max_price: float
    alert_max_price_crypto: float
    log_level: str
    # Polymarket Data API (real signals)
    signal_source: str  # polymarket | demo
    polymarket_data_api_base: str
    polymarket_trades_limit: int
    polymarket_max_trade_age_sec: int
    # Startup backfill (catch-up missed trades after downtime)
    polymarket_backfill_enabled: bool
    polymarket_backfill_age_sec: int
    polymarket_backfill_limit: int
    polymarket_backfill_max_pages: int
    polymarket_resolution_enabled: bool
    polymarket_resolution_poll_interval_sec: int
    polymarket_resolution_batch_size: int
    polymarket_gamma_api_base: str
    trader_stats_enabled: bool
    trader_stats_positions_limit: int
    trader_stats_cache_ttl_sec: int
    admin_user_ids: tuple[int, ...]
    persistence_mode: str  # memory | sqlite
    sqlite_db_path: str

    def whale_threshold_for_category(self, category: str) -> int:
        if category == "Crypto":
            return self.whale_threshold_crypto_usd
        return self.whale_threshold_usd

    def api_whale_fetch_threshold_usd(self) -> int:
        return min(self.whale_threshold_usd, self.whale_threshold_crypto_usd)


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
        whale_threshold_crypto_usd=int(os.getenv("WHALE_THRESHOLD_CRYPTO", "20000")),
        signal_poll_interval_sec=int(os.getenv("SIGNAL_POLL_INTERVAL_SEC", "30")),
        alert_max_price=float(os.getenv("ALERT_MAX_PRICE", "0.95")),
        alert_max_price_crypto=float(os.getenv("ALERT_MAX_PRICE_CRYPTO", "0.999")),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        signal_source=_normalize_signal_source(os.getenv("SIGNAL_SOURCE", "polymarket")),
        polymarket_data_api_base=os.getenv(
            "POLYMARKET_DATA_API_BASE", "https://data-api.polymarket.com"
        ).rstrip("/"),
        polymarket_trades_limit=int(os.getenv("POLYMARKET_TRADES_LIMIT", "100")),
        polymarket_max_trade_age_sec=int(os.getenv("POLYMARKET_MAX_TRADE_AGE_SEC", "600")),
        polymarket_backfill_enabled=(os.getenv("POLYMARKET_BACKFILL_ENABLED", "true").strip().lower() in ("1", "true", "yes", "y", "on")),
        polymarket_backfill_age_sec=int(os.getenv("POLYMARKET_BACKFILL_AGE_SEC", str(24 * 3600))),
        polymarket_backfill_limit=int(os.getenv("POLYMARKET_BACKFILL_LIMIT", "200")),
        polymarket_backfill_max_pages=int(os.getenv("POLYMARKET_BACKFILL_MAX_PAGES", "8")),
        polymarket_resolution_enabled=(
            os.getenv("POLYMARKET_RESOLUTION_ENABLED", "true").strip().lower()
            in ("1", "true", "yes", "y", "on")
        ),
        polymarket_resolution_poll_interval_sec=int(
            os.getenv("POLYMARKET_RESOLUTION_POLL_INTERVAL_SEC", "120")
        ),
        polymarket_resolution_batch_size=int(
            os.getenv("POLYMARKET_RESOLUTION_BATCH_SIZE", "25")
        ),
        polymarket_gamma_api_base=os.getenv(
            "POLYMARKET_GAMMA_API_BASE", "https://gamma-api.polymarket.com"
        ).rstrip("/"),
        trader_stats_enabled=(
            os.getenv("TRADER_STATS_ENABLED", "true").strip().lower()
            in ("1", "true", "yes", "y", "on")
        ),
        trader_stats_positions_limit=int(os.getenv("TRADER_STATS_POSITIONS_LIMIT", "100")),
        trader_stats_cache_ttl_sec=int(os.getenv("TRADER_STATS_CACHE_TTL_SEC", "3600")),
        admin_user_ids=_parse_admin_user_ids(os.getenv("ADMIN_USER_IDS", "")),
        persistence_mode=os.getenv("PERSISTENCE_MODE", "sqlite").strip().lower(),
        sqlite_db_path=os.getenv(
            "SQLITE_DB_PATH",
            # relative to Bot/ directory by default
            str(Path(__file__).resolve().parent.parent / "data" / "bot.sqlite3"),
        ),
    )
