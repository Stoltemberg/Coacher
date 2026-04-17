from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .match_analyzer import expected_cs


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
) -> list[EconomySignal]:
    if not hardcore_enabled or game_time <= 300:
        return []

    minutes = game_time / 60.0
    expected_cs_value = expected_cs(minutes)
    signals: list[EconomySignal] = []

    if creep_score < (expected_cs_value * 0.6):
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
    elif creep_score > expected_cs_value:
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

    if minutes >= 10 and ward_score < 5:
        signals.append(
            EconomySignal(
                metric="vision",
                score=0.22,
                note=f"Visão fraca com {ward_score} de ward score aos {int(minutes)} minutos.",
                category="macro",
                severity="negative",
                actual=ward_score,
                target="Comprar controle e preparar entradas antes do rio.",
            )
        )

    return signals
