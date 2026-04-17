from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


def _topic_from_signal(category: str | None, severity: str | None, metadata: dict[str, Any] | None) -> str | None:
    normalized = str(category or "").strip().lower()
    metric = str((metadata or {}).get("metric") or "").strip().lower()

    if normalized in {"farm_eval"} or metric == "farm":
        return "farm"
    if normalized in {"vision_eval"} or metric == "vision":
        return "vision"
    if normalized in {"item_advice", "build_plan"} or metric == "itemization":
        return "itemization"
    if normalized in {"dragon", "baron", "herald", "horde", "turret", "inhibitor"}:
        return "objective_setup"
    if normalized in {"self_death", "self_kill", "enemy_death", "ally_death", "multikill", "first_blood"}:
        return "fight_discipline"
    if normalized in {"opening_plan", "lane_matchup"} and severity == "negative":
        return "lane_control"
    return None


def resolve_adaptive_topic(category: str | None, severity: str | None, metadata: dict[str, Any] | None = None) -> str | None:
    topic = _topic_from_signal(category, severity, metadata)
    if topic:
        return topic

    normalized = str(category or "").strip().lower()
    if normalized in {"opening_plan", "lane_matchup"}:
        return "lane_control"
    return None


@dataclass(slots=True)
class AdaptiveCue:
    topic: str
    mode: str
    streak: int
    game_time: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class TopicTrend:
    negative_streak: int = 0
    positive_streak: int = 0
    last_negative_time: float | None = None
    last_positive_time: float | None = None
    last_feedback_time: float | None = None
    recovery_pending: bool = False
    last_feedback_streak: int = 0


class AdaptiveTracker:
    """Tracks repeated live problems and detects real corrections."""

    def __init__(self) -> None:
        self._topics: dict[str, TopicTrend] = {}

    def reset(self) -> None:
        self._topics.clear()

    def snapshot(self) -> dict[str, dict[str, Any]]:
        return {
            topic: {
                "negative_streak": trend.negative_streak,
                "positive_streak": trend.positive_streak,
                "last_negative_time": trend.last_negative_time,
                "last_positive_time": trend.last_positive_time,
                "recovery_pending": trend.recovery_pending,
            }
            for topic, trend in self._topics.items()
        }

    def ingest(
        self,
        *,
        category: str | None,
        severity: str | None,
        game_time: float | None,
        metadata: dict[str, Any] | None = None,
    ) -> AdaptiveCue | None:
        normalized_severity = str(severity or "").strip().lower()
        if normalized_severity not in {"positive", "negative"}:
            return None

        topic = _topic_from_signal(category, normalized_severity, metadata)
        if not topic:
            return None

        second_mark = max(0.0, float(game_time or 0.0))
        trend = self._topics.setdefault(topic, TopicTrend())

        if normalized_severity == "negative":
            return self._ingest_negative(topic, trend, second_mark, metadata or {})
        return self._ingest_positive(topic, trend, second_mark, metadata or {})

    def _ingest_negative(
        self,
        topic: str,
        trend: TopicTrend,
        second_mark: float,
        metadata: dict[str, Any],
    ) -> AdaptiveCue | None:
        if trend.last_negative_time is not None and (second_mark - trend.last_negative_time) > self._window(topic):
            trend.negative_streak = 0
            trend.last_feedback_streak = 0

        trend.negative_streak += 1
        trend.positive_streak = 0
        trend.last_negative_time = second_mark
        trend.recovery_pending = True

        threshold = self._negative_threshold(topic, metadata)
        if trend.negative_streak < threshold:
            return None

        if trend.last_feedback_time is not None and (second_mark - trend.last_feedback_time) < self._feedback_cooldown(topic):
            return None

        if trend.negative_streak <= trend.last_feedback_streak:
            return None

        trend.last_feedback_time = second_mark
        trend.last_feedback_streak = trend.negative_streak
        return AdaptiveCue(
            topic=topic,
            mode="escalation",
            streak=trend.negative_streak,
            game_time=second_mark,
            metadata=dict(metadata),
        )

    def _ingest_positive(
        self,
        topic: str,
        trend: TopicTrend,
        second_mark: float,
        metadata: dict[str, Any],
    ) -> AdaptiveCue | None:
        trend.positive_streak += 1
        trend.last_positive_time = second_mark

        if not trend.recovery_pending:
            if trend.negative_streak > 0:
                trend.negative_streak = 0
                trend.last_feedback_streak = 0
            return None

        if trend.negative_streak < 2:
            trend.negative_streak = 0
            trend.last_feedback_streak = 0
            trend.recovery_pending = False
            return None

        if trend.last_negative_time is not None and (second_mark - trend.last_negative_time) > self._recovery_window(topic):
            trend.negative_streak = 0
            trend.last_feedback_streak = 0
            trend.recovery_pending = False
            return None

        if trend.last_feedback_time is not None and (second_mark - trend.last_feedback_time) < max(35.0, self._feedback_cooldown(topic) / 2):
            return None

        prior_streak = trend.negative_streak
        trend.negative_streak = 0
        trend.last_feedback_streak = 0
        trend.last_feedback_time = second_mark
        trend.recovery_pending = False
        return AdaptiveCue(
            topic=topic,
            mode="recovery",
            streak=prior_streak,
            game_time=second_mark,
            metadata=dict(metadata),
        )

    def _negative_threshold(self, topic: str, metadata: dict[str, Any]) -> int:
        priority = str(metadata.get("priority") or "").strip().lower()
        if priority in {"high", "critical"}:
            return 2
        if topic in {"fight_discipline", "itemization", "objective_setup"}:
            return 2
        return 3

    def _window(self, topic: str) -> float:
        if topic == "farm":
            return 720.0
        if topic in {"vision", "objective_setup"}:
            return 540.0
        return 420.0

    def _recovery_window(self, topic: str) -> float:
        if topic == "farm":
            return 900.0
        return self._window(topic)

    def _feedback_cooldown(self, topic: str) -> float:
        if topic == "fight_discipline":
            return 120.0
        if topic == "objective_setup":
            return 180.0
        return 150.0
