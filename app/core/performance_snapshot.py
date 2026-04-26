from __future__ import annotations

from typing import Any


ROLE_TARGETS: dict[str, dict[str, float]] = {
    "top": {"farm": 0.7, "vision": 0.55, "objective_setup": 0.58, "fight_discipline": 0.62},
    "jungle": {"farm": 0.64, "vision": 0.66, "objective_setup": 0.72, "fight_discipline": 0.64},
    "mid": {"farm": 0.72, "vision": 0.58, "objective_setup": 0.6, "fight_discipline": 0.64},
    "bottom": {"farm": 0.76, "vision": 0.52, "objective_setup": 0.58, "fight_discipline": 0.66},
    "support": {"farm": 0.2, "vision": 0.78, "objective_setup": 0.68, "fight_discipline": 0.64},
}

METRIC_LABELS = {
    "farm": "Farm",
    "vision": "Visao",
    "objective_setup": "Objetivos",
    "fight_discipline": "Decisao",
    "itemization": "Build",
    "lane_control": "Lane",
}


def _round_score(value: Any) -> float:
    try:
        return round(float(value), 3)
    except (TypeError, ValueError):
        return 0.0


def build_performance_snapshot(history_snapshot: dict[str, Any], player_profile: dict[str, Any]) -> dict[str, Any]:
    role = str((player_profile or {}).get("primary_role") or "mid").strip().lower()
    targets = ROLE_TARGETS.get(role, ROLE_TARGETS["mid"])
    avg_scores = dict(history_snapshot.get("avg_scores") or {})
    matches_played = int(history_snapshot.get("matches_played") or 0)
    wins = int(history_snapshot.get("wins") or 0)

    if matches_played <= 0:
        return {
            "headline": "Sem partidas registradas ainda",
            "matches_played": 0,
            "record": "Sem historico",
            "win_rate": 0.0,
            "role": role,
            "goal": (player_profile or {}).get("player_goal") or "subir_elo",
            "metrics": [],
            "strongest_areas": [],
            "focus_areas": [],
        }

    metrics = []
    for metric_id, target in targets.items():
        if metric_id not in avg_scores:
            continue
        current = _round_score(avg_scores.get(metric_id))
        delta = round(current - target, 3)
        metrics.append(
            {
                "id": metric_id,
                "label": METRIC_LABELS.get(metric_id, metric_id.replace("_", " ").title()),
                "current": current,
                "target": target,
                "delta": delta,
                "status": "ahead" if delta >= 0.04 else "close" if delta >= -0.04 else "behind",
            }
        )

    metrics.sort(key=lambda item: item["delta"])
    win_rate = round(wins / matches_played, 3) if matches_played > 0 else 0.0

    headline = history_snapshot.get("headline") or "Sem leitura suficiente ainda"
    if not metrics:
        headline = "Historico encontrado, mas ainda sem telemetria suficiente"

    return {
        "headline": headline,
        "matches_played": matches_played,
        "record": history_snapshot.get("record") or "0W - 0L",
        "win_rate": win_rate,
        "role": role,
        "goal": (player_profile or {}).get("player_goal") or "subir_elo",
        "metrics": metrics,
        "strongest_areas": list((history_snapshot.get("recurring_strengths") or [])[:3]),
        "focus_areas": list((history_snapshot.get("recurring_improvements") or [])[:3]),
    }
