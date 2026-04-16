"""Player memory and post-game summary helpers for Coacher.

This module is intentionally isolated so it can be wired into the current
coach loop later without forcing changes in the rest of the codebase.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Any, Iterable, Optional

from .memory_store import MemoryStore


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _normalize_token(value: Any, default: str = "general") -> str:
    token = _normalize_text(value).lower().replace(" ", "_")
    return token or default


def _as_float(value: Any, default: Optional[float] = None) -> Optional[float]:
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def _unique_in_order(items: Iterable[str]) -> list[str]:
    seen = set()
    out = []
    for item in items:
        if not item:
            continue
        if item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out


def _parse_datetime(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    try:
        parsed = datetime.fromisoformat(str(value))
    except (TypeError, ValueError):
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


@dataclass(slots=True)
class MemoryEntry:
    """Single item stored in the player's memory."""

    kind: str
    text: str
    timestamp: datetime
    phase: str = "unknown"
    category: str = "general"
    severity: str = "neutral"
    importance: float = 0.5
    tags: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "text": self.text,
            "timestamp": self.timestamp.isoformat(),
            "phase": self.phase,
            "category": self.category,
            "severity": self.severity,
            "importance": self.importance,
            "tags": list(self.tags),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MemoryEntry":
        return cls(
            kind=_normalize_token(data.get("kind"), "event"),
            text=_normalize_text(data.get("text")),
            timestamp=_parse_datetime(data.get("timestamp")) or _utc_now(),
            phase=_normalize_token(data.get("phase"), "unknown"),
            category=_normalize_token(data.get("category"), "general"),
            severity=_normalize_token(data.get("severity"), "neutral"),
            importance=_clamp(_as_float(data.get("importance"), 0.5) or 0.5),
            tags=tuple(
                _normalize_token(tag, "")
                for tag in (data.get("tags") or [])
                if _normalize_text(tag)
            ),
            metadata=dict(data.get("metadata") or {}),
        )


@dataclass(slots=True)
class MatchMemory:
    """Current match state plus the trail of recorded entries."""

    match_id: Optional[str] = None
    player_name: Optional[str] = None
    champion_name: Optional[str] = None
    role: Optional[str] = None
    started_at: datetime = field(default_factory=_utc_now)
    ended_at: Optional[datetime] = None
    result: Optional[str] = None
    context: dict[str, Any] = field(default_factory=dict)
    entries: list[MemoryEntry] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "match_id": self.match_id,
            "player_name": self.player_name,
            "champion_name": self.champion_name,
            "role": self.role,
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "result": self.result,
            "context": dict(self.context),
            "entries": [entry.to_dict() for entry in self.entries],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MatchMemory":
        return cls(
            match_id=data.get("match_id"),
            player_name=data.get("player_name"),
            champion_name=data.get("champion_name"),
            role=data.get("role"),
            started_at=_parse_datetime(data.get("started_at")) or _utc_now(),
            ended_at=_parse_datetime(data.get("ended_at")),
            result=_normalize_token(data.get("result"), "unknown") if data.get("result") else None,
            context=dict(data.get("context") or {}),
            entries=[
                MemoryEntry.from_dict(entry)
                for entry in (data.get("entries") or [])
                if isinstance(entry, dict)
            ],
        )

    def duration_seconds(self, end_time: Optional[datetime] = None) -> float:
        end_time = end_time or self.ended_at or _utc_now()
        return max(0.0, (end_time - self.started_at).total_seconds())


@dataclass(slots=True)
class PostGameSummary:
    """Structured post-game output generated from player memory."""

    headline: str
    opening: str
    strengths: list[str]
    improvements: list[str]
    key_moments: list[str]
    next_steps: list[str]
    stats: dict[str, Any]
    coach_note: str
    player_name: Optional[str] = None
    champion_name: Optional[str] = None
    role: Optional[str] = None
    result: Optional[str] = None
    generated_at: datetime = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "headline": self.headline,
            "opening": self.opening,
            "strengths": list(self.strengths),
            "improvements": list(self.improvements),
            "key_moments": list(self.key_moments),
            "next_steps": list(self.next_steps),
            "stats": dict(self.stats),
            "coach_note": self.coach_note,
            "player_name": self.player_name,
            "champion_name": self.champion_name,
            "role": self.role,
            "result": self.result,
            "generated_at": self.generated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PostGameSummary":
        return cls(
            headline=_normalize_text(data.get("headline")),
            opening=_normalize_text(data.get("opening")),
            strengths=[_normalize_text(item) for item in data.get("strengths") or [] if _normalize_text(item)],
            improvements=[_normalize_text(item) for item in data.get("improvements") or [] if _normalize_text(item)],
            key_moments=[_normalize_text(item) for item in data.get("key_moments") or [] if _normalize_text(item)],
            next_steps=[_normalize_text(item) for item in data.get("next_steps") or [] if _normalize_text(item)],
            stats=dict(data.get("stats") or {}),
            coach_note=_normalize_text(data.get("coach_note")),
            player_name=data.get("player_name"),
            champion_name=data.get("champion_name"),
            role=data.get("role"),
            result=data.get("result"),
            generated_at=_parse_datetime(data.get("generated_at")) or _utc_now(),
        )

    def to_text(self) -> str:
        lines = [self.headline, self.opening]

        if self.strengths:
            lines.append("Pontos fortes:")
            lines.extend(f"- {item}" for item in self.strengths)

        if self.improvements:
            lines.append("Ajustes prioritarios:")
            lines.extend(f"- {item}" for item in self.improvements)

        if self.key_moments:
            lines.append("Momentos-chave:")
            lines.extend(f"- {item}" for item in self.key_moments)

        if self.next_steps:
            lines.append("Proximo treino:")
            lines.extend(f"- {item}" for item in self.next_steps)

        lines.append(self.coach_note)
        return "\n".join(lines)


class PlayerMemory:
    """Stores match events, evaluations and post-game coaching memory."""

    def __init__(
        self,
        player_name: Optional[str] = None,
        champion_name: Optional[str] = None,
        role: Optional[str] = None,
        intensity: str = "standard",
        storage_path: str | Path | None = None,
        autosave: bool = True,
        load_from_disk: bool = True,
    ):
        self._lock = RLock()
        self._store = MemoryStore.default(storage_path)
        self._autosave = bool(autosave)

        self.player_name = player_name
        self.champion_name = champion_name
        self.role = role
        self.intensity = _normalize_token(intensity, "standard")
        self.history: list[MatchMemory] = []
        self.current_match = MatchMemory(
            player_name=player_name,
            champion_name=champion_name,
            role=role,
        )

        if load_from_disk:
            self.reload()

        if player_name is not None:
            self.player_name = player_name
        if champion_name is not None:
            self.champion_name = champion_name
        if role is not None:
            self.role = role

        self.current_match.player_name = self.player_name
        self.current_match.champion_name = self.champion_name
        self.current_match.role = self.role

    @property
    def storage_path(self) -> Path:
        return self._store.path

    def set_intensity(self, intensity: str) -> None:
        with self._lock:
            self.intensity = _normalize_token(intensity, "standard")
            self._touch_storage()

    def configure_storage(self, storage_path: str | Path | None) -> None:
        with self._lock:
            self._store = MemoryStore.default(storage_path)
            self.reload()

    def save(self) -> bool:
        with self._lock:
            return self._store.save(self.snapshot())

    def reload(self) -> bool:
        with self._lock:
            payload = self._store.load()
            if payload is None:
                return False
            self._apply_snapshot(payload)
            return True

    load_from_disk = reload
    save_to_disk = save

    def snapshot(self) -> dict[str, Any]:
        return {
            "player_name": self.player_name,
            "champion_name": self.champion_name,
            "role": self.role,
            "intensity": self.intensity,
            "current_match": self.current_match.to_dict(),
            "history": [match.to_dict() for match in self.history],
        }

    def to_dict(self) -> dict[str, Any]:
        return self.snapshot()

    def clear_history(self) -> None:
        with self._lock:
            self.history.clear()
            self._touch_storage()

    def reset_current_match(self) -> None:
        self.current_match = MatchMemory(
            player_name=self.player_name,
            champion_name=self.champion_name,
            role=self.role,
        )
        self._touch_storage()

    def _apply_snapshot(self, payload: dict[str, Any]) -> None:
        self.player_name = payload.get("player_name", self.player_name)
        self.champion_name = payload.get("champion_name", self.champion_name)
        self.role = payload.get("role", self.role)
        self.intensity = _normalize_token(payload.get("intensity", self.intensity), "standard")

        history_payload = payload.get("history") or []
        self.history = [
            MatchMemory.from_dict(match)
            for match in history_payload
            if isinstance(match, dict)
        ]

        current_payload = payload.get("current_match")
        if isinstance(current_payload, dict):
            self.current_match = MatchMemory.from_dict(current_payload)
        else:
            self.current_match = MatchMemory(
                player_name=self.player_name,
                champion_name=self.champion_name,
                role=self.role,
            )

    def _touch_storage(self) -> None:
        if self._autosave:
            self._store.save(self.snapshot())

    def _archive_current_match(self) -> None:
        self.history.append(self.current_match)
        self.reset_current_match()

    def start_match(
        self,
        *,
        player_name: Optional[str] = None,
        champion_name: Optional[str] = None,
        role: Optional[str] = None,
        match_id: Optional[str] = None,
        context: Optional[dict[str, Any]] = None,
        started_at: Optional[datetime] = None,
        clear_current: bool = True,
    ) -> None:
        with self._lock:
            if self.current_match.entries:
                self._archive_current_match()
            elif clear_current and self.current_match.result is not None:
                self._archive_current_match()

            self.current_match = MatchMemory(
                match_id=match_id,
                player_name=player_name if player_name is not None else self.player_name,
                champion_name=champion_name if champion_name is not None else self.champion_name,
                role=role if role is not None else self.role,
                started_at=started_at or _utc_now(),
                context=dict(context or {}),
            )
            self._touch_storage()

    def record_event(
        self,
        kind: str,
        text: str,
        *,
        phase: Optional[str] = None,
        category: Optional[str] = None,
        severity: str = "neutral",
        importance: float = 0.5,
        tags: Optional[Iterable[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
    ) -> MemoryEntry:
        with self._lock:
            entry = MemoryEntry(
                kind=_normalize_token(kind, "event"),
                text=_normalize_text(text),
                timestamp=timestamp or _utc_now(),
                phase=_normalize_token(phase, "unknown") if phase else "unknown",
                category=_normalize_token(category, "general"),
                severity=_normalize_token(severity, "neutral"),
                importance=_clamp(_as_float(importance, 0.5) or 0.5),
                tags=tuple(
                    _normalize_token(tag, "")
                    for tag in (tags or ())
                    if _normalize_text(tag)
                ),
                metadata=dict(metadata or {}),
            )
            self.current_match.entries.append(entry)
            self._touch_storage()
            return entry

    def record_evaluation(
        self,
        metric: str,
        score: Optional[float] = None,
        *,
        note: Optional[str] = None,
        phase: Optional[str] = None,
        category: Optional[str] = None,
        expected: Optional[float] = None,
        actual: Optional[float] = None,
        target: Optional[str] = None,
        severity: Optional[str] = None,
        importance: float = 0.8,
        tags: Optional[Iterable[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
    ) -> MemoryEntry:
        payload = dict(metadata or {})
        payload.update(
            {
                "metric": _normalize_token(metric, "metric"),
                "score": _as_float(score),
                "expected": _as_float(expected),
                "actual": _as_float(actual),
                "target": _normalize_text(target) or None,
            }
        )
        if note:
            payload["note"] = _normalize_text(note)

        entry_severity = severity
        if entry_severity is None:
            if score is not None:
                numeric_score = _as_float(score, 0.0) or 0.0
                if numeric_score >= 0.7:
                    entry_severity = "positive"
                elif numeric_score <= 0.4:
                    entry_severity = "negative"
                else:
                    entry_severity = "neutral"
            else:
                entry_severity = "neutral"

        return self.record_event(
            "evaluation",
            note or f"Avaliacao de {metric}",
            phase=phase,
            category=category or metric,
            severity=entry_severity,
            importance=importance,
            tags=tags,
            metadata=payload,
            timestamp=timestamp,
        )

    def record_note(
        self,
        text: str,
        *,
        severity: str = "info",
        phase: Optional[str] = None,
        category: Optional[str] = None,
        importance: float = 0.3,
        tags: Optional[Iterable[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
    ) -> MemoryEntry:
        return self.record_event(
            "note",
            text,
            phase=phase,
            category=category or "note",
            severity=severity,
            importance=importance,
            tags=tags,
            metadata=metadata,
            timestamp=timestamp,
        )

    def end_match(
        self,
        *,
        result: Optional[str] = None,
        ended_at: Optional[datetime] = None,
        keep_history: bool = True,
        archive_current: bool = True,
    ) -> PostGameSummary:
        with self._lock:
            if result is not None:
                self.current_match.result = _normalize_token(result, "unknown")
            self.current_match.ended_at = ended_at or _utc_now()

            summary = self.generate_postgame_summary()
            if archive_current or keep_history:
                self.history.append(self.current_match)
            self.reset_current_match()
            self._touch_storage()
            return summary

    def generate_postgame_summary(
        self,
        *,
        result: Optional[str] = None,
        max_strengths: int = 4,
        max_improvements: int = 4,
        max_key_moments: int = 5,
    ) -> PostGameSummary:
        match = self.current_match
        entries = list(match.entries)
        final_result = _normalize_token(result or match.result, "unknown")
        if not entries:
            return PostGameSummary(
                headline=self._headline(final_result, empty=True),
                opening=self._opening(final_result, empty=True),
                strengths=["Nao houve registro suficiente para fechar uma leitura decente dessa partida."],
                improvements=["Liga a memoria do coach na proxima partida para eu enxergar tua execucao de verdade."],
                key_moments=[],
                next_steps=["Registrar kills, objetivos, notas de farm e erros recorrentes durante a partida."],
                stats={"entries": 0, "events": 0, "evaluations": 0, "notes": 0},
                coach_note=self._coach_note(final_result, empty=True),
                player_name=match.player_name,
                champion_name=match.champion_name,
                role=match.role,
                result=final_result,
            )

        severity_counts = Counter(entry.severity for entry in entries)
        kind_counts = Counter(entry.kind for entry in entries)
        category_counts = Counter(entry.category for entry in entries)

        evaluations = [entry for entry in entries if entry.kind == "evaluation"]
        score_buckets: dict[str, list[float]] = defaultdict(list)
        for entry in evaluations:
            metric = _normalize_token(entry.metadata.get("metric"), entry.category)
            score = _as_float(entry.metadata.get("score"))
            if score is not None:
                score_buckets[metric].append(score)

        avg_scores = {
            metric: round(sum(values) / len(values), 3)
            for metric, values in score_buckets.items()
            if values
        }

        strengths = self._derive_strengths(entries, avg_scores, max_strengths)
        improvements = self._derive_improvements(entries, avg_scores, max_improvements)
        key_moments = self._derive_key_moments(entries, max_key_moments)
        next_steps = self._derive_next_steps(improvements, avg_scores, final_result)

        stats = {
            "entries": len(entries),
            "events": kind_counts.get("event", 0),
            "evaluations": len(evaluations),
            "notes": kind_counts.get("note", 0),
            "positive": severity_counts.get("positive", 0),
            "negative": severity_counts.get("negative", 0),
            "neutral": severity_counts.get("neutral", 0),
            "top_categories": category_counts.most_common(5),
            "avg_scores": avg_scores,
            "duration_seconds": round(match.duration_seconds(), 1),
        }

        return PostGameSummary(
            headline=self._headline(final_result),
            opening=self._opening(final_result),
            strengths=strengths,
            improvements=improvements,
            key_moments=key_moments,
            next_steps=next_steps,
            stats=stats,
            coach_note=self._coach_note(final_result),
            player_name=match.player_name,
            champion_name=match.champion_name,
            role=match.role,
            result=final_result,
        )

    def build_history_snapshot(
        self,
        *,
        limit_matches: int = 8,
        limit_patterns: int = 4,
        limit_recent: int = 6,
    ) -> dict[str, Any]:
        with self._lock:
            matches = self._completed_matches(limit_matches)
            if not matches:
                return {
                    "matches_played": 0,
                    "wins": 0,
                    "losses": 0,
                    "record": "0W - 0L",
                    "headline": "Sem historico suficiente ainda",
                    "recurring_strengths": [],
                    "recurring_improvements": [],
                    "recent_memory": [],
                }

            wins = sum(1 for match in matches if match.result == "win")
            losses = sum(1 for match in matches if match.result == "loss")

            metric_scores: dict[str, list[float]] = defaultdict(list)
            negative_categories = Counter()
            positive_categories = Counter()
            recent_memory: list[dict[str, str]] = []

            for match in reversed(matches):
                match_name = self._match_display_name(match)
                summary = self._summarize_match_for_history(match)
                if summary:
                    recent_memory.append(
                        {
                            "title": match_name,
                            "note": summary["note"],
                            "tone": summary["tone"],
                        }
                    )

                for entry in match.entries:
                    metric = _normalize_token(entry.metadata.get("metric"), "")
                    score = _as_float(entry.metadata.get("score"))
                    if metric and score is not None:
                        metric_scores[metric].append(score)

                    if entry.severity == "negative":
                        negative_categories[entry.category] += 1
                    elif entry.severity == "positive":
                        positive_categories[entry.category] += 1

            avg_scores = {
                metric: round(sum(values) / len(values), 3)
                for metric, values in metric_scores.items()
                if values
            }

            recurring_strengths = self._derive_recurring_strengths(
                avg_scores, positive_categories, limit_patterns
            )
            recurring_improvements = self._derive_recurring_improvements(
                avg_scores, negative_categories, limit_patterns
            )

            return {
                "matches_played": len(matches),
                "wins": wins,
                "losses": losses,
                "record": f"{wins}W - {losses}L",
                "headline": self._history_headline(wins, losses, len(matches)),
                "recurring_strengths": recurring_strengths,
                "recurring_improvements": recurring_improvements,
                "recent_memory": recent_memory[:limit_recent],
            }

    def _completed_matches(self, limit_matches: int) -> list[MatchMemory]:
        completed = [
            match
            for match in self.history
            if match.entries and (match.ended_at is not None or match.result is not None)
        ]
        if limit_matches <= 0:
            return completed
        return completed[-limit_matches:]

    def _match_display_name(self, match: MatchMemory) -> str:
        champion = _normalize_text(match.champion_name) or "Campeao"
        role = _normalize_text(match.role)
        result = _normalize_token(match.result, "unknown")
        result_map = {
            "win": "Vitoria",
            "loss": "Derrota",
            "completed": "Concluida",
            "unknown": "Analise",
        }
        label = result_map.get(result, "Analise")
        if role:
            return f"{label} com {champion} ({role})"
        return f"{label} com {champion}"

    def _summarize_match_for_history(self, match: MatchMemory) -> Optional[dict[str, str]]:
        if not match.entries:
            return None

        top_entry = max(
            match.entries,
            key=lambda entry: (entry.importance, entry.timestamp),
        )
        tone = "positive" if top_entry.severity == "positive" else "negative" if top_entry.severity == "negative" else "system"
        return {
            "note": top_entry.text,
            "tone": tone,
        }

    def _derive_recurring_strengths(
        self,
        avg_scores: dict[str, float],
        positive_categories: Counter,
        limit_patterns: int,
    ) -> list[str]:
        strengths: list[str] = []

        for metric, score in sorted(avg_scores.items(), key=lambda item: item[1], reverse=True):
            if score < 0.68:
                continue
            strengths.append(self._metric_strength_phrase(metric, score))

        for category, count in positive_categories.most_common():
            if len(strengths) >= limit_patterns:
                break
            strengths.append(self._category_strength_phrase(category, count))

        if not strengths:
            strengths.append("Ainda nao tem padrao positivo forte o bastante para chamar de assinatura tua.")

        return _unique_in_order(strengths)[:limit_patterns]

    def _derive_recurring_improvements(
        self,
        avg_scores: dict[str, float],
        negative_categories: Counter,
        limit_patterns: int,
    ) -> list[str]:
        improvements: list[str] = []

        for metric, score in sorted(avg_scores.items(), key=lambda item: item[1]):
            if score > 0.58:
                continue
            improvements.append(self._metric_improvement_phrase(metric, score))

        for category, count in negative_categories.most_common():
            if len(improvements) >= limit_patterns:
                break
            improvements.append(self._category_improvement_phrase(category, count))

        if not improvements:
            improvements.append("Nao apareceu um vazamento recorrente claro, entao o proximo passo e consolidar consistencia.")

        return _unique_in_order(improvements)[:limit_patterns]

    def _history_headline(self, wins: int, losses: int, matches_played: int) -> str:
        if matches_played <= 0:
            return "Sem historico suficiente ainda"
        if wins > losses:
            return "Tua memoria recente mostra mais acerto do que desastre, mas ainda com arestas claras."
        if losses > wins:
            return "O historico recente ta te denunciando mais pelos erros repetidos do que pelos acertos."
        return "Teu historico recente ta equilibrado, entao a diferenca vai nascer dos detalhes que tu repetir melhor."

    def _headline(self, result: str, empty: bool = False) -> str:
        if empty:
            return "Resumo de partida: memoria insuficiente"
        if result == "win":
            return "Resumo da partida: venceu, mas sem luxo"
        if result == "loss":
            return "Resumo da partida: tomou a licao e agora corrige"
        return "Resumo da partida: leitura finalizada"

    def _opening(self, result: str, empty: bool = False) -> str:
        tone = "hardcore" if self.intensity == "hardcore" else "standard"
        if empty:
            if tone == "hardcore":
                return "Sem dados de verdade, entao nao inventa historia. Na proxima, deixa eu ver a partida inteira."
            return "Sem registro suficiente para fechar leitura de jogo. Na proxima partida, me alimenta com mais contexto."

        if result == "win":
            if tone == "hardcore":
                return "Ganhou, mas nao foi passe livre. Tem coisa boa aqui e tem coisa torta que ainda pode te ferrar em jogo apertado."
            return "Boa, venceu. Agora a parte adulta do processo e ver o que te fez ganhar e o que ainda pode te quebrar em jogo duro."
        if result == "loss":
            if tone == "hardcore":
                return "Perdeu porque a partida cobrou tua execucao em varios pontos. Vamos separar o que foi erro de leitura e o que foi pura desorganizacao."
            return "Perdeu, mas isso nao e desculpa pra ignorar a leitura. A partida deixou claro onde tu entregou vantagem e onde precisa ajustar."
        if tone == "hardcore":
            return "Partida fechada. Vamos cortar o ruido e olhar o que te fez jogar certo, o que te derrubou e o que precisa mudar ja."
        return "Partida fechada. Agora vem a leitura honesta do que funcionou, do que falhou e do que fazer diferente na proxima."

    def _coach_note(self, result: str, empty: bool = False) -> str:
        if empty:
            return "Sem memoria nao existe coaching. Registra melhor a proxima partida e eu te entrego uma leitura de verdade."

        if self.intensity == "hardcore":
            if result == "win":
                return "Tu ganhou, mas nao se ilude: o processo ainda tem buraco. Corrige agora, porque jogar no limite sem disciplina cobra caro depois."
            if result == "loss":
                return "Tu perdeu e a conta veio limpa. Usa essa dor como mapa, porque repetir o mesmo erro e burrice, nao azar."
            return "Sem resultado claro, mas a execucao falou. Agora para de romantizar a partida e ajusta o que precisa antes da proxima fila."

        if result == "win":
            return "Vitoria boa, mas o valor real esta em transformar esse jogo em padrao repetivel. Mantem o que funcionou e corrige o resto."
        if result == "loss":
            return "Derrota util quando vira aprendizado. Se tu corrigir as tres falhas mais pesadas, a proxima partida ja muda de cara."
        return "A partida terminou e o que importa agora e converter isso em habito, nao em memoria solta."

    def _derive_strengths(
        self,
        entries: list[MemoryEntry],
        avg_scores: dict[str, float],
        max_strengths: int,
    ) -> list[str]:
        strengths: list[str] = []

        for metric, score in sorted(avg_scores.items(), key=lambda item: item[1], reverse=True):
            if score < 0.7:
                continue
            strengths.append(self._metric_strength_phrase(metric, score))

        positive_categories = Counter(entry.category for entry in entries if entry.severity == "positive")
        for category, count in positive_categories.most_common():
            if len(strengths) >= max_strengths:
                break
            strengths.append(self._category_strength_phrase(category, count))

        if not strengths:
            strengths.append("Nao houve um padrao forte de vantagem, mas tu pelo menos manteve a partida viva sem colapsar de vez.")

        return _unique_in_order(strengths)[:max_strengths]

    def _derive_improvements(
        self,
        entries: list[MemoryEntry],
        avg_scores: dict[str, float],
        max_improvements: int,
    ) -> list[str]:
        improvements: list[str] = []

        for metric, score in sorted(avg_scores.items(), key=lambda item: item[1]):
            if score > 0.6:
                continue
            improvements.append(self._metric_improvement_phrase(metric, score))

        negative_categories = Counter(entry.category for entry in entries if entry.severity == "negative")
        for category, count in negative_categories.most_common():
            if len(improvements) >= max_improvements:
                break
            improvements.append(self._category_improvement_phrase(category, count))

        if not improvements:
            improvements.append("A partida nao mostrou buraco grande, entao o foco agora e parar de repetir os bons habitos de forma aleatoria.")

        return _unique_in_order(improvements)[:max_improvements]

    def _derive_key_moments(
        self,
        entries: list[MemoryEntry],
        max_key_moments: int,
    ) -> list[str]:
        scored = sorted(
            entries,
            key=lambda entry: (
                entry.importance,
                1 if entry.severity == "positive" else 0,
                entry.timestamp,
            ),
            reverse=True,
        )

        moments = []
        for entry in scored:
            prefix = self._entry_prefix(entry)
            moments.append(f"{prefix}{entry.text}")
            if len(moments) >= max_key_moments:
                break

        return moments

    def _derive_next_steps(
        self,
        improvements: list[str],
        avg_scores: dict[str, float],
        result: str,
    ) -> list[str]:
        next_steps: list[str] = []

        for improvement in improvements[:3]:
            next_steps.append(self._improvement_to_action(improvement))

        if "farm" in avg_scores or "cs" in avg_scores:
            next_steps.append("Cria meta de farm por minuto e cobra wave antes de cacar luta.")
        if "vision" in avg_scores:
            next_steps.append("Reorganiza setup de visao antes de avancar no rio ou side.")
        if result == "loss":
            next_steps.append("Rever as mortes mais caras e transformar cada uma em gatilho de disciplina.")
        elif result == "win":
            next_steps.append("Repete a parte boa sem inventar moda, porque ganho sem consistencia vira sorte.")

        if not next_steps:
            next_steps.append("Registra mais eventos e avaliacoes para eu transformar a proxima partida em leitura util.")

        return _unique_in_order(next_steps)[:5]

    def _entry_prefix(self, entry: MemoryEntry) -> str:
        if entry.severity == "positive":
            return "Boa: "
        if entry.severity == "negative":
            return "Ponto fraco: "
        return "Registro: "

    def _metric_strength_phrase(self, metric: str, score: float) -> str:
        metric = metric.lower()
        if metric in {"farm", "cs", "creep_score", "creepscore"}:
            return "Teu farm ficou acima da media, com leitura de wave mais consistente e melhor transformacao de recurso."
        if metric in {"vision", "ward", "warding"}:
            return "A visao ficou relativamente forte, com setup mais consciente e menos entrada cega."
        if metric in {"objective", "objetivo", "macro"}:
            return "O macro apareceu bem e tu conseguiu converter espaco em objetivo em boa parte da partida."
        if metric in {"fight", "teamfight", "combat"}:
            return "As lutas tiveram leitura boa e tu impactou nas janelas mais importantes."
        return f"A metrica {metric} sustentou um desempenho bom com media {score:.2f}."

    def _metric_improvement_phrase(self, metric: str, score: float) -> str:
        metric = metric.lower()
        if metric in {"farm", "cs", "creep_score", "creepscore"}:
            return "Farm fraco abaixo do aceitavel. Para de perder wave e trata minion como dinheiro vivo."
        if metric in {"vision", "ward", "warding"}:
            return "Visao insuficiente. Sem ward e controle, tu joga no escuro e entrega vantagem de graca."
        if metric in {"death", "deaths", "survivability"}:
            return "Posicionamento e sobrevivencia precisam de ajuste urgente. Morrer demais desmonta qualquer plano."
        if metric in {"objective", "objetivo", "macro"}:
            return "Setup de objetivo abaixo do ideal. Chega no rio antes, porque improviso ganha pouco e perde muito."
        if metric in {"fight", "teamfight", "combat"}:
            return "Execucao de luta abaixo do esperado. Tu precisa entrar com timing, nao com ansiedade."
        return f"A metrica {metric} ficou fraca demais, com media {score:.2f}, entao merece revisao imediata."

    def _category_strength_phrase(self, category: str, count: int) -> str:
        category = category.lower()
        if category == "dragon":
            return "Tu controlou dragao bem e converteu essa pressao em vantagem de mapa."
        if category in {"baron", "horde", "herald", "turret", "inhibitor"}:
            return "A leitura de estrutura ficou boa e abriu caminho para vantagem concreta."
        if category in {"self_kill", "enemy_death", "multikill"}:
            return "Tu puniu bem os erros e soube converter fight em recurso real."
        if category == "farm_eval":
            return "Teu controle de farm sustentou a partida em varios trechos."
        if category == "vision_eval":
            return "A disciplina de visao ajudou a ler melhor o mapa."
        return f"O padrao positivo de {category} apareceu {count} vezes e segurou tua partida."

    def _category_improvement_phrase(self, category: str, count: int) -> str:
        category = category.lower()
        if category in {"self_death", "ally_death"}:
            return "Mortes demais em zona errada. Tu precisa respeitar melhor o risco antes de entrar."
        if category == "farm_eval":
            return "Faltou disciplina de farm em varios momentos. Wave ruim vira jogo ruim."
        if category == "vision_eval":
            return "Visao foi subestimada. Sem setup, tu entra no mapa e vira alvo facil."
        if category == "item_advice":
            return "Build e adaptacao ainda estao atrasadas. Se o inimigo troca o perfil, tua loja tambem tem que trocar."
        if category == "minimap":
            return "Leitura do minimapa foi inconsistente. Olhar o mapa nao e opcional."
        if category == "macro":
            return "Macro ficou fraca em varios trechos. Ganhar espaco e nao converter e desperdicio puro."
        return f"O padrao negativo de {category} apareceu {count} vezes e merece prioridade."

    def _improvement_to_action(self, improvement: str) -> str:
        lower = improvement.lower()
        if "farm" in lower:
            return "Treina wave e last hit ate virar reflexo, porque dinheiro no chao nao ganha jogo."
        if "visao" in lower or "vision" in lower:
            return "Fecha controle e pensa rota de ward antes de andar no escuro."
        if "morte" in lower or "morrer" in lower or "posicionamento" in lower:
            return "Segura o ego, respeita cooldown e para de entregar pick gratis."
        if "macro" in lower:
            return "Joga por tempo e estrutura, nao por impulso."
        if "luta" in lower or "fight" in lower:
            return "Entra em fight com setup e numero, nao na fome."
        return "Revisar essa area antes da proxima fila."


__all__ = [
    "MemoryEntry",
    "MatchMemory",
    "PlayerMemory",
    "PostGameSummary",
]
