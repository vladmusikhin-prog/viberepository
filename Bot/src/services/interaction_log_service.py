from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from aiogram import Bot

from src.config import Settings

logger = logging.getLogger(__name__)

TELEGRAM_MESSAGE_LIMIT = 4096


@dataclass
class UserSnapshot:
    telegram_user_id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None

    def display_name(self) -> str:
        parts = [p for p in (self.first_name, self.last_name) if p]
        if parts:
            return " ".join(parts)
        if self.username:
            return self.username
        return str(self.telegram_user_id)

    def username_label(self) -> str:
        if self.username:
            return f"@{self.username}"
        return "—"


@dataclass
class SessionAction:
    action: str
    at_ts: float
    detail: Optional[str] = None
    user_text: Optional[str] = None


@dataclass
class InteractionSession:
    user: UserSnapshot
    started_at: float
    last_at: float
    actions: List[SessionAction] = field(default_factory=list)


def _format_time_utc(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%H:%M:%S")


def _format_duration_minutes(start_ts: float, end_ts: float) -> str:
    minutes = max(0.0, end_ts - start_ts) / 60.0
    return f"{minutes:.1f} minutes"


def _format_timeline_line(action: SessionAction) -> str:
    line = f"   {_format_time_utc(action.at_ts)} → {action.action}"
    if action.detail:
        line += f" ({action.detail})"
    return line


def _truncate_market(title: str, max_len: int = 48) -> str:
    cleaned = (title or "").strip()
    if len(cleaned) <= max_len:
        return cleaned
    return cleaned[: max_len - 1] + "…"


def format_session_report(
    session: InteractionSession,
    *,
    categories: List[str],
    is_live_enabled: bool,
) -> str:
    user = session.user
    duration = _format_duration_minutes(session.started_at, session.last_at)
    total_actions = len(session.actions)

    lines = [
        "🐋 Whale Signals Bot Logs",
        "",
        "👤 USER INTERACTION REPORT",
        f"🆔 User: {user.telegram_user_id} ({user.display_name()}) {user.username_label()}",
        f"🌐 Language: {user.language_code or '—'}",
        f"⏱️ Session Duration: {duration}",
        f"🔄 Total Actions: {total_actions}",
        "",
        "📋 ACTION TIMELINE:",
    ]
    for action in session.actions:
        lines.append(_format_timeline_line(action))

    user_requests = [a for a in session.actions if a.user_text]
    if user_requests:
        lines.extend(["", "💬 USER REQUESTS:"])
        for action in user_requests:
            text = action.user_text or ""
            lines.append(f"   {_format_time_utc(action.at_ts)}: \"{text}\"")
            lines.append(f"   └─ Action: {action.action}")

    whale_count = sum(1 for a in session.actions if a.action == "alert_whale_delivered")
    resolution_count = sum(
        1 for a in session.actions if a.action == "alert_resolution_delivered"
    )
    categories_label = ", ".join(categories) if categories else "—"
    live_label = "live enabled" if is_live_enabled else "live disabled"
    outcome_parts = [live_label, f"categories: {categories_label}"]
    if whale_count:
        outcome_parts.append(f"whale alerts: {whale_count}")
    if resolution_count:
        outcome_parts.append(f"resolution alerts: {resolution_count}")

    lines.extend(["", f"⭐️ Session outcome: {' · '.join(outcome_parts)}"])

    report = "\n".join(lines)
    if len(report) > TELEGRAM_MESSAGE_LIMIT:
        report = report[: TELEGRAM_MESSAGE_LIMIT - 20] + "\n… (truncated)"
    return report


class InteractionLogService:
    def __init__(
        self,
        bot: Bot,
        settings: Settings,
        user_repo,
    ) -> None:
        self._bot = bot
        self._settings = settings
        self._user_repo = user_repo
        self._sessions: Dict[int, InteractionSession] = {}

    @property
    def is_active(self) -> bool:
        return (
            self._settings.analytics_enabled
            and self._settings.analytics_chat_id is not None
        )

    async def record_action(
        self,
        user_id: int,
        action: str,
        *,
        detail: Optional[str] = None,
        user_text: Optional[str] = None,
        user_snapshot: Optional[UserSnapshot] = None,
    ) -> None:
        if not self.is_active:
            return

        await self.flush_expired_sessions()

        now = time.time()
        session = self._sessions.get(user_id)
        if session is None:
            if user_snapshot is None:
                user_snapshot = UserSnapshot(telegram_user_id=user_id)
            session = InteractionSession(
                user=user_snapshot,
                started_at=now,
                last_at=now,
            )
            self._sessions[user_id] = session
        else:
            session.last_at = now
            if user_snapshot is not None:
                session.user = user_snapshot

        session.actions.append(
            SessionAction(
                action=action,
                at_ts=now,
                detail=detail,
                user_text=user_text,
            )
        )

    async def flush_expired_sessions(self) -> None:
        if not self.is_active:
            return

        now = time.time()
        timeout = self._settings.analytics_session_timeout_sec
        expired = [
            user_id
            for user_id, session in self._sessions.items()
            if now - session.last_at >= timeout
        ]
        for user_id in expired:
            await self._flush_session(user_id)

    async def flush_all_sessions(self) -> None:
        if not self.is_active:
            return
        for user_id in list(self._sessions.keys()):
            await self._flush_session(user_id)

    async def _flush_session(self, user_id: int) -> None:
        session = self._sessions.pop(user_id, None)
        if session is None or not session.actions:
            return

        user = self._user_repo.get_or_create(user_id)
        report = format_session_report(
            session,
            categories=list(user.categories),
            is_live_enabled=user.is_live_enabled,
        )
        chat_id = self._settings.analytics_chat_id
        if chat_id is None:
            return
        try:
            await self._bot.send_message(chat_id=chat_id, text=report)
        except Exception:  # noqa: BLE001
            logger.warning(
                "Failed to post interaction log for user_id=%s",
                user_id,
                exc_info=True,
            )

    async def record_whale_alert_delivered(
        self,
        user_id: int,
        *,
        category: str,
        market_title: str,
        size_usd: float,
    ) -> None:
        detail = f"{category}, ${size_usd:,.0f}, {_truncate_market(market_title)}"
        await self.record_action(
            user_id,
            "alert_whale_delivered",
            detail=detail,
        )

    async def record_resolution_alert_delivered(
        self,
        user_id: int,
        *,
        outcome: str,
        market_title: str,
    ) -> None:
        detail = f"{outcome}, {_truncate_market(market_title)}"
        await self.record_action(
            user_id,
            "alert_resolution_delivered",
            detail=detail,
        )
