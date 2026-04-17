from __future__ import annotations

from dataclasses import dataclass, field


DEFAULT_CATEGORY_FILTERS = {
    "draft": True,
    "lane": True,
    "macro": True,
    "objective": True,
    "economy": True,
    "recovery": True,
}


CATEGORY_BUCKETS = {
    "draft": "draft",
    "identity": "draft",
    "lane_matchup": "lane",
    "assist": "lane",
    "self_kill": "lane",
    "self_death": "recovery",
    "ally_death": "recovery",
    "enemy_death": "lane",
    "first_blood": "lane",
    "multikill": "recovery",
    "macro": "macro",
    "minimap": "macro",
    "mid_game_job": "macro",
    "jungle_intel": "macro",
    "dragon": "objective",
    "baron": "objective",
    "herald": "objective",
    "horde": "objective",
    "turret": "objective",
    "inhibitor": "objective",
    "build_plan": "economy",
    "power_spike": "economy",
    "farm_eval": "economy",
    "item_advice": "economy",
    "opening_plan": "lane",
    "vision_eval": "macro",
    "adaptive_feedback": "recovery",
}


def map_call_category(category: str | None) -> str | None:
    if not category:
        return None
    return CATEGORY_BUCKETS.get(str(category).strip().lower())


@dataclass(slots=True)
class CoachSettings:
    voice_enabled: bool = True
    objectives_enabled: bool = True
    intensity: str = "standard"
    voice_preset: str = "standard"
    category_filters: dict[str, bool] = field(
        default_factory=lambda: dict(DEFAULT_CATEGORY_FILTERS)
    )

    def set_preset(self, preset: str) -> None:
        normalized = (preset or "standard").strip().lower()
        if normalized not in {"standard", "hardcore", "minimal"}:
            normalized = "standard"

        self.voice_preset = normalized
        self.intensity = "hardcore" if normalized == "hardcore" else "standard"

    def is_category_enabled(self, category: str | None) -> bool:
        bucket = map_call_category(category)
        if not bucket:
            return True
        return bool(self.category_filters.get(bucket, True))


@dataclass(slots=True)
class MatchState:
    coaching_active: bool = False
    current_phase: str = "lobby"
    coach_mode: str = "draft"
    active_player_name: str | None = None
    current_champion_name: str | None = None
    our_team: str = "ORDER"
    my_position: str = ""
    game_time: float = 0.0
    current_assists: int = -1
    last_farm_eval: float = 0.0
    lane_matchup_announced: bool = False
    detailed_matchup_announced: bool = False
    early_build_plan_announced: bool = False
    opening_plan_announced: bool = False
    mid_game_job_announced: bool = False
    ally_drags: int = 0
    enemy_drags: int = 0
    match_started: bool = False
    match_finalized: bool = False
    last_summary: object | None = None
    last_item_check: float = 0.0
    player_to_champ: dict[str, str] = field(default_factory=dict)
    player_to_team: dict[str, str] = field(default_factory=dict)
    player_to_role: dict[str, str] = field(default_factory=dict)
    advised_items: set[str] = field(default_factory=set)
    last_announced_at: dict[str, float] = field(default_factory=dict)
