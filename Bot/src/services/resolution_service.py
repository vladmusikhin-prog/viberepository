from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Literal, Optional

from src.models.entities import TrackedMarket, utc_now
from src.services.texts import format_resolution_text

logger = logging.getLogger(__name__)

WhaleResult = Literal["win", "loss", "split", "exit_win", "exit_loss"]


@dataclass(frozen=True)
class MarketResolution:
    winning_outcome: Optional[str]
    is_split: bool
    closed_time: Optional[str]


@dataclass(frozen=True)
class WhaleOutcomeAssessment:
    result: WhaleResult
    pnl_usd: float
    note: str


class ResolutionService:
    WINNER_PRICE_THRESHOLD = 0.99
    SPLIT_PRICE_TOLERANCE = 0.02

    def __init__(self, pending_repo) -> None:
        self.pending_repo = pending_repo

    def resolution_signal_id(self, condition_id: str) -> str:
        return f"pm-res-{condition_id}"

    def track_whale_trade(
        self,
        trade: dict[str, Any],
        category: str,
        placement_signal_id: str,
    ) -> bool:
        condition_id = str(trade.get("conditionId") or "").strip()
        if not condition_id:
            return False

        slug = str(trade.get("slug") or "")
        title = str(trade.get("title") or "Unknown market")
        trade_side = str(trade.get("side") or "").upper()
        outcome = str(trade.get("outcome") or "")
        try:
            price = float(trade.get("price") or 0.0)
        except (TypeError, ValueError):
            price = 0.0
        try:
            size_usd = float(trade.get("size") or 0.0)
        except (TypeError, ValueError):
            size_usd = 0.0
        ts_raw = trade.get("timestamp")
        try:
            trade_timestamp = int(ts_raw) if ts_raw is not None else 0
        except (TypeError, ValueError):
            trade_timestamp = 0

        tracked = TrackedMarket(
            condition_id=condition_id,
            slug=slug,
            title=title,
            category=category,
            trade_side=trade_side,
            outcome=outcome,
            price=price,
            size_usd=size_usd,
            placement_signal_id=placement_signal_id,
            trade_timestamp=trade_timestamp,
            created_at=utc_now(),
        )
        return self.pending_repo.track_if_new(tracked)

    def parse_market_resolution(self, market: dict[str, Any]) -> Optional[MarketResolution]:
        if not market.get("closed"):
            return None

        outcomes = self._parse_json_list(market.get("outcomes"))
        prices = self._parse_price_list(market.get("outcomePrices"))
        if not outcomes or not prices or len(outcomes) != len(prices):
            return None

        max_price = max(prices)
        if all(abs(price - 0.5) <= self.SPLIT_PRICE_TOLERANCE for price in prices):
            closed_time = self._format_closed_time(market.get("closedTime"))
            return MarketResolution(
                winning_outcome=None,
                is_split=True,
                closed_time=closed_time,
            )

        if max_price < self.WINNER_PRICE_THRESHOLD:
            status = str(market.get("umaResolutionStatus") or "").lower()
            if status != "resolved":
                return None

        winner_idx = prices.index(max_price)
        winning_outcome = outcomes[winner_idx]
        closed_time = self._format_closed_time(market.get("closedTime"))
        return MarketResolution(
            winning_outcome=winning_outcome,
            is_split=False,
            closed_time=closed_time,
        )

    def assess_whale_outcome(
        self,
        tracked: TrackedMarket,
        resolution: MarketResolution,
    ) -> WhaleOutcomeAssessment:
        side = tracked.trade_side.upper()
        price = tracked.price
        size = tracked.size_usd

        if resolution.is_split:
            return WhaleOutcomeAssessment(
                result="split",
                pnl_usd=0.0,
                note="Рынок закрыт с исходом 50/50.",
            )

        winning = resolution.winning_outcome or ""
        whale_outcome = tracked.outcome
        whale_won = whale_outcome == winning

        if side == "BUY":
            if whale_won:
                pnl = size * (1.0 / price - 1.0) if price > 0 else 0.0
                return WhaleOutcomeAssessment(
                    result="win",
                    pnl_usd=pnl,
                    note="Ставка кита совпала с итоговым исходом.",
                )
            return WhaleOutcomeAssessment(
                result="loss",
                pnl_usd=-size,
                note="Ставка кита не совпала с итоговым исходом.",
            )

        # SELL — кит вышел из позиции до исхода
        if whale_won:
            missed = size * (1.0 / price - 1.0) if price > 0 else 0.0
            return WhaleOutcomeAssessment(
                result="exit_loss",
                pnl_usd=-missed,
                note="Кит продал до исхода; победившая сторона продолжала расти.",
            )
        kept = size * (1.0 - price) / price if price > 0 else 0.0
        return WhaleOutcomeAssessment(
            result="exit_win",
            pnl_usd=kept,
            note="Кит продал до исхода; позиция обесценилась после продажи.",
        )

    def build_resolution_alert(
        self,
        tracked: TrackedMarket,
        resolution: MarketResolution,
    ) -> tuple[str, str]:
        assessment = self.assess_whale_outcome(tracked, resolution)
        side_label = f"{tracked.trade_side} {tracked.outcome}".strip()
        text = format_resolution_text(
            market=tracked.title,
            whale_side=side_label,
            size_usd=tracked.size_usd,
            price=tracked.price,
            winning_outcome=resolution.winning_outcome,
            is_split=resolution.is_split,
            result=assessment.result,
            pnl_usd=assessment.pnl_usd,
            note=assessment.note,
            closed_time=resolution.closed_time,
            category=tracked.category,
        )
        return self.resolution_signal_id(tracked.condition_id), text

    def _parse_json_list(self, raw: Any) -> list[str]:
        if isinstance(raw, list):
            return [str(item) for item in raw]
        if not raw:
            return []
        try:
            parsed = json.loads(str(raw))
        except (TypeError, ValueError, json.JSONDecodeError):
            return []
        if not isinstance(parsed, list):
            return []
        return [str(item) for item in parsed]

    def _parse_price_list(self, raw: Any) -> list[float]:
        items = self._parse_json_list(raw) if isinstance(raw, str) else []
        if not items and isinstance(raw, list):
            items = [str(v) for v in raw]
        prices: list[float] = []
        for item in items:
            try:
                prices.append(float(item))
            except (TypeError, ValueError):
                prices.append(0.0)
        return prices

    def _format_closed_time(self, raw: Any) -> Optional[str]:
        if not raw:
            return None
        text = str(raw).strip()
        if not text:
            return None
        for fmt in ("%Y-%m-%d %H:%M:%S%z", "%Y-%m-%dT%H:%M:%S%z"):
            try:
                dt = datetime.strptime(text.replace("+00", "+0000"), fmt)
                return dt.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            except ValueError:
                continue
        return text[:16]
