from dataclasses import dataclass

from aiogram import Bot

from src.config import Settings
from src.services.admin_service import AdminService
from src.services.interaction_log_service import InteractionLogService
from src.services.resolution_service import ResolutionService
from src.services.settings_service import SettingsService
from src.services.signal_service import SignalService
from src.services.trader_stats_service import TraderStatsService
from src.services.user_service import UserService
from src.repositories.in_memory import SignalRepository as InMemorySignalRepository
from src.repositories.in_memory import UserRepository as InMemoryUserRepository
from src.repositories.pending_resolution_repo import (
    InMemoryPendingResolutionRepository,
    SQLitePendingResolutionRepository,
)
from src.repositories.sqlite_repo import SQLiteSignalRepository, SQLiteUserRepository


@dataclass
class AppContext:
    user_service: UserService
    signal_service: SignalService
    trader_stats_service: TraderStatsService
    resolution_service: ResolutionService
    settings_service: SettingsService
    admin_service: AdminService
    interaction_log_service: InteractionLogService


def build_context(settings: Settings, bot: Bot) -> AppContext:
    if settings.persistence_mode == "sqlite":
        user_repo = SQLiteUserRepository(settings.sqlite_db_path)
        signal_repo = SQLiteSignalRepository(settings.sqlite_db_path)
        pending_resolution_repo = SQLitePendingResolutionRepository(settings.sqlite_db_path)
    else:
        user_repo = InMemoryUserRepository()
        signal_repo = InMemorySignalRepository()
        pending_resolution_repo = InMemoryPendingResolutionRepository()

    user_service = UserService(user_repo)
    signal_service = SignalService(
        user_repo=user_repo,
        signal_repo=signal_repo,
        whale_threshold_usd=settings.whale_threshold_usd,
        whale_threshold_crypto_usd=settings.whale_threshold_crypto_usd,
        whale_threshold_economics_usd=settings.whale_threshold_economics_usd,
        bot_username=settings.bot_username,
        trader_stats_positions_limit=settings.trader_stats_positions_limit,
    )
    trader_stats_service = TraderStatsService(
        enabled=settings.trader_stats_enabled,
        positions_limit=settings.trader_stats_positions_limit,
        cache_ttl_sec=settings.trader_stats_cache_ttl_sec,
        data_api_base=settings.polymarket_data_api_base,
    )
    resolution_service = ResolutionService(pending_resolution_repo)
    settings_service = SettingsService(user_repo)
    admin_service = AdminService(user_repo, signal_repo, settings.admin_user_ids)
    interaction_log_service = InteractionLogService(
        bot=bot,
        settings=settings,
        user_repo=user_repo,
    )
    return AppContext(
        user_service=user_service,
        signal_service=signal_service,
        trader_stats_service=trader_stats_service,
        resolution_service=resolution_service,
        settings_service=settings_service,
        admin_service=admin_service,
        interaction_log_service=interaction_log_service,
    )
