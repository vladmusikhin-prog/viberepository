from dataclasses import dataclass

from src.repositories.in_memory import SignalRepository, UserRepository
from src.services.feedback_service import FeedbackService
from src.services.settings_service import SettingsService
from src.services.signal_service import SignalService
from src.services.user_service import UserService


@dataclass
class AppContext:
    user_service: UserService
    signal_service: SignalService
    feedback_service: FeedbackService
    settings_service: SettingsService


def build_context(whale_threshold_usd: int, bot_username: str) -> AppContext:
    user_repo = UserRepository()
    signal_repo = SignalRepository()
    user_service = UserService(user_repo)
    signal_service = SignalService(
        user_repo=user_repo,
        signal_repo=signal_repo,
        whale_threshold_usd=whale_threshold_usd,
        bot_username=bot_username,
    )
    feedback_service = FeedbackService(user_repo)
    settings_service = SettingsService(user_repo)
    return AppContext(
        user_service=user_service,
        signal_service=signal_service,
        feedback_service=feedback_service,
        settings_service=settings_service,
    )
