from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .match_analyzer import expected_cs


ROLE_CS_PER_MINUTE = {
    "top": 6.6,
    "jungle": 5.3,
    "mid": 6.8,
    "bottom": 7.2,
    "support": 1.2,
}

ROLE_VISION_PER_MINUTE = {
    "top": 1.0,
    "jungle": 1.25,
    "mid": 1.0,
    "bottom": 0.9,
    "support": 1.8,
}


@dataclass(slots=True)
class EconomySignal:
    metric: str
    score: float
    note: str
    category: str
    severity: str
    actual: float | None = None
    expected: float | None = None
    target: str | None = None


def build_enemy_team_names(
    player_to_team: dict[str, str],
    player_to_champ: dict[str, str],
    our_team: str,
) -> list[str]:
    return [
        player_to_champ.get(player_name)
        for player_name, team_name in player_to_team.items()
        if team_name != our_team and player_to_champ.get(player_name)
    ]


def find_lane_enemy(
    players_data: list[dict[str, Any]],
    our_team: str,
    my_position: str,
) -> dict[str, Any] | None:
    if not my_position or my_position == "NONE":
        return None

    for player in players_data:
        if player.get("team") != our_team and player.get("position") == my_position:
            return player
    return None


def analyze_economy(
    *,
    game_time: float,
    creep_score: int,
    ward_score: float,
    hardcore_enabled: bool,
    role: str | None = None,
    farm_threshold: float = 0.6,
    vision_threshold: float = 5.0,
) -> list[EconomySignal]:
    if not hardcore_enabled or game_time <= 300:
        return []

    minutes = game_time / 60.0
    role_key = str(role or "").strip().lower()
    expected_cs_value = expected_cs(minutes, cs_per_minute=ROLE_CS_PER_MINUTE.get(role_key, 6.5))
    effective_vision_threshold = max(vision_threshold, ROLE_VISION_PER_MINUTE.get(role_key, 1.0) * minutes)
    signals: list[EconomySignal] = []

    if role_key != "support" and creep_score < (expected_cs_value * farm_threshold):
        signals.append(
            EconomySignal(
                metric="farm",
                score=0.25,
                note=f"Farm abaixo do ideal: {creep_score} CS aos {int(minutes)} minutos.",
                category="economy",
                severity="negative",
                actual=creep_score,
                expected=round(expected_cs_value, 1),
            )
        )
    elif role_key != "support" and creep_score > expected_cs_value:
        signals.append(
            EconomySignal(
                metric="farm",
                score=0.82,
                note=f"Farm forte: {creep_score} CS aos {int(minutes)} minutos.",
                category="economy",
                severity="positive",
                actual=creep_score,
                expected=round(expected_cs_value, 1),
            )
        )

    if minutes >= 10 and ward_score < effective_vision_threshold:
        signals.append(
            EconomySignal(
                metric="vision",
                score=0.22,
                note=f"Visão fraca com {ward_score} de ward score aos {int(minutes)} minutos.",
                category="macro",
                severity="negative",
                actual=ward_score,
                target="Comprar controle e preparar entradas antes do rio."
                if role_key != "support"
                else "Suporte precisa liderar visão e setup de objetivo.",
            )
        )
    elif role_key == "support" and minutes >= 10 and ward_score >= (effective_vision_threshold * 1.15):
        signals.append(
            EconomySignal(
                metric="vision",
                score=0.85,
                note=f"Visão forte para suporte: {ward_score} de ward score aos {int(minutes)} minutos.",
                category="macro",
                severity="positive",
                actual=ward_score,
                target="Continua liderando setup de visão e cobertura de objetivo.",
            )
        )

    return signals
