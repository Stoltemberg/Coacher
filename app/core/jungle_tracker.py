from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


def _clean_name(value: Any) -> str:
    text = str(value or "").strip()
    return text.split("#")[0].strip()


def _clean_role(value: Any) -> str:
    return str(value or "").strip().upper()


def _event_time(event: dict[str, Any], fallback: float) -> float:
    try:
        return float(event.get("EventTime", fallback))
    except (TypeError, ValueError):
        return float(fallback or 0.0)


def _format_clock(seconds: float | None) -> str:
    if seconds is None:
        return "--:--"
    total_seconds = max(0, int(seconds))
    minutes, remainder = divmod(total_seconds, 60)
    return f"{minutes:02d}:{remainder:02d}"


def _lane_from_role(role: str) -> str:
    normalized = _clean_role(role)
    if normalized in {"TOP"}:
        return "topo"
    if normalized in {"BOTTOM", "ADC", "UTILITY", "SUPPORT"}:
        return "bot"
    if normalized in {"MIDDLE", "MID"}:
        return "mid"
    if normalized in {"JUNGLE"}:
        return "selva"
    return "rio"


@dataclass(slots=True)
class JungleIntel:
    enemy_jungler_name: str | None = None
    enemy_jungler_champion: str | None = None
    our_jungler_name: str | None = None
    last_seen_at: float | None = None
    last_seen_source: str | None = None
    probable_side: str = "unknown"
    confidence: float = 0.1
    first_gank: dict[str, Any] | None = None
    objective_presence: dict[str, int] = field(
        default_factory=lambda: {"dragon": 0, "herald": 0, "baron": 0, "horde": 0}
    )
    notes: list[dict[str, Any]] = field(default_factory=list)
    last_impacted_lane: str = "unknown"


class JungleTracker:
    def __init__(self) -> None:
        self.intel = JungleIntel()

    def reset(self) -> None:
        self.intel = JungleIntel()

    def ingest_roster(
        self,
        players_data: list[dict[str, Any]],
        our_team: str,
        active_player_name: str | None,
        game_time: float,
        player_to_role: dict[str, str],
        player_to_team: dict[str, str],
        player_to_champ: dict[str, str],
    ) -> None:
        if not active_player_name:
            return

        for player in players_data:
            player_name = _clean_name(player.get("summonerName"))
            if not player_name:
                continue

            role = _clean_role(player.get("position"))
            team = str(player.get("team") or player_to_team.get(player_name) or "")
            champion = str(player.get("championName") or player_to_champ.get(player_name) or "")

            if role == "JUNGLE" and team == our_team:
                self.intel.our_jungler_name = player_name
            elif role == "JUNGLE" and team and team != our_team:
                self.intel.enemy_jungler_name = player_name
                self.intel.enemy_jungler_champion = champion or self.intel.enemy_jungler_champion
                if self.intel.last_seen_at is None:
                    self.intel.last_seen_at = game_time
                    self.intel.last_seen_source = "roster"

        self._refresh_confidence()

    def ingest_event(
        self,
        event: dict[str, Any],
        game_time: float,
        player_to_role: dict[str, str],
        player_to_team: dict[str, str],
        player_to_champ: dict[str, str],
    ) -> None:
        name = str(event.get("EventName") or "").strip()
        if not name:
            return

        event_time = _event_time(event, game_time)
        enemy_jungler = self.intel.enemy_jungler_name
        if not enemy_jungler:
            return

        if name == "ChampionKill":
            self._ingest_kill_event(
                event,
                event_time,
                enemy_jungler,
                player_to_role,
                player_to_team,
            )
        elif name in {"DragonKill", "HeraldKill", "BaronKill", "HordeKill"}:
            self._ingest_objective_event(event, event_time, enemy_jungler, player_to_champ)

        self._refresh_confidence()

    def snapshot(self) -> dict[str, Any]:
        first_gank = dict(self.intel.first_gank) if self.intel.first_gank else None
        notes = [dict(note) for note in self.intel.notes[:6]]
        return {
            "enemy_jungler_name": self.intel.enemy_jungler_name,
            "enemy_jungler_champion": self.intel.enemy_jungler_champion,
            "our_jungler_name": self.intel.our_jungler_name,
            "last_seen_at": self.intel.last_seen_at,
            "last_seen_clock": _format_clock(self.intel.last_seen_at),
            "last_seen_source": self.intel.last_seen_source,
            "probable_side": self.intel.probable_side,
            "confidence": round(self.intel.confidence, 2),
            "first_gank": first_gank,
            "objective_presence": dict(self.intel.objective_presence),
            "notes": notes,
            "last_impacted_lane": self.intel.last_impacted_lane,
        }

    def _ingest_kill_event(
        self,
        event: dict[str, Any],
        event_time: float,
        enemy_jungler: str,
        player_to_role: dict[str, str],
        player_to_team: dict[str, str],
    ) -> None:
        killer = _clean_name(event.get("KillerName"))
        victim = _clean_name(event.get("VictimName"))
        assisters = [_clean_name(name) for name in event.get("Assisters", []) if _clean_name(name)]
        if enemy_jungler not in {killer, *assisters}:
            return

        victim_role = player_to_role.get(victim, "")
        victim_team = player_to_team.get(victim)
        lane = _lane_from_role(victim_role)
        if lane == "selva":
            lane = "rio"

        self.intel.last_seen_at = event_time
        self.intel.last_seen_source = "champion_kill"
        self.intel.probable_side = "top" if lane == "topo" else "bot" if lane == "bot" else "river"
        self.intel.last_impacted_lane = lane

        if self.intel.first_gank is None and victim_role not in {"", "JUNGLE"}:
            self.intel.first_gank = {
                "lane": lane,
                "clock": _format_clock(event_time),
                "event_time": event_time,
                "target_team": "ally" if victim_team and victim_team != player_to_team.get(enemy_jungler) else "enemy",
            }

        target = "pressionou tua lane" if self.intel.first_gank and self.intel.first_gank.get("target_team") == "ally" else f"impactou {lane}"
        self._push_note(
            title="Jungler inimigo apareceu",
            detail=f"{enemy_jungler} apareceu em {lane} e {target}.",
            event_time=event_time,
            tone="warning" if victim_team and victim_team != player_to_team.get(enemy_jungler) else "system",
        )

    def _ingest_objective_event(
        self,
        event: dict[str, Any],
        event_time: float,
        enemy_jungler: str,
        player_to_champ: dict[str, str],
    ) -> None:
        killer = _clean_name(event.get("KillerName"))
        if killer != enemy_jungler:
            return

        name = str(event.get("EventName") or "").strip()
        objective_key = {
            "DragonKill": "dragon",
            "HeraldKill": "herald",
            "BaronKill": "baron",
            "HordeKill": "horde",
        }.get(name)
        if not objective_key:
            return

        self.intel.objective_presence[objective_key] = self.intel.objective_presence.get(objective_key, 0) + 1
        self.intel.last_seen_at = event_time
        self.intel.last_seen_source = name.lower()
        if objective_key == "dragon":
            self.intel.probable_side = "bot"
        elif objective_key in {"herald", "baron"}:
            self.intel.probable_side = "top"
        else:
            self.intel.probable_side = "river"

        champion = player_to_champ.get(enemy_jungler) or self.intel.enemy_jungler_champion or "o jungler inimigo"
        label = {
            "dragon": "dragão",
            "herald": "Arauto",
            "baron": "Barão",
            "horde": "larvas",
        }[objective_key]
        self._push_note(
            title="Pressão de selva",
            detail=f"{champion} já apareceu no {label}. Dá para assumir presença forte desse lado do mapa.",
            event_time=event_time,
            tone="urgent" if objective_key in {"dragon", "baron"} else "warning",
        )

    def _push_note(self, title: str, detail: str, event_time: float, tone: str = "system") -> None:
        note = {
            "title": title,
            "detail": detail,
            "clock": _format_clock(event_time),
            "event_time": event_time,
            "tone": tone,
        }
        self.intel.notes.insert(0, note)
        self.intel.notes = self.intel.notes[:6]

    def _refresh_confidence(self) -> None:
        signals = 0
        if self.intel.enemy_jungler_name:
            signals += 1
        if self.intel.first_gank:
            signals += 1
        signals += sum(1 for value in self.intel.objective_presence.values() if value)
        if self.intel.last_seen_source and self.intel.last_seen_source != "roster":
            signals += 1
        self.intel.confidence = min(0.95, 0.2 + (signals * 0.15))
