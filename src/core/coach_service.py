from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from .coach_analyzer import EconomySignal, analyze_economy, build_enemy_team_names
from .event_analyzer import (
    EventAnalysis,
    analyze_champion_kill,
    analyze_first_blood,
    analyze_multikill,
    analyze_objective_event,
    analyze_structure_event,
)


@dataclass(slots=True)
class DraftPackage:
    champion: str
    power_spikes: list[str]
    comp_style: str
    pressure_points: list[str]
    build_focus: list[str]
    lane_plan: str
    first_reset_focus: str
    opening_plan: str
    mid_game_job: str
    situational_items: list[str]
    duo_synergy: Optional[dict[str, Any]] = None
    jungle_synergy: Optional[dict[str, Any]] = None


class CoachService:
    def __init__(self, knowledge=None):
        self.knowledge = knowledge

    def build_draft_package(
        self,
        my_champion: Any,
        enemy_team: list[Any],
        *,
        allies: list[dict[str, Any]] | None = None,
        role: str | None = None,
    ) -> Optional[DraftPackage]:
        if not self.knowledge:
            return None

        guidance = self.knowledge.get_draft_guidance(my_champion, enemy_team, role=role)
        if not guidance:
            return None

        duo_synergy = None
        jungle_synergy = None
        if allies:
            duo_synergy = self._resolve_duo_synergy(my_champion, allies, role)
            jungle_synergy = self._resolve_jungle_synergy(my_champion, allies, role)

        return DraftPackage(
            champion=guidance.get("champion", ""),
            power_spikes=list(guidance.get("power_spikes", [])),
            comp_style=guidance.get("comp_style", "comp equilibrada"),
            pressure_points=list(guidance.get("pressure_points", [])),
            build_focus=list(guidance.get("build_focus", [])),
            lane_plan=guidance.get("lane_plan", ""),
            first_reset_focus=guidance.get("first_reset_focus", ""),
            opening_plan=guidance.get("opening_plan", ""),
            mid_game_job=guidance.get("mid_game_job", ""),
            situational_items=list(guidance.get("situational_items", [])),
            duo_synergy=duo_synergy,
            jungle_synergy=jungle_synergy,
        )

    def build_live_package(
        self,
        my_champion: Any,
        player_to_team: dict[str, str],
        player_to_champ: dict[str, str],
        *,
        our_team: str,
        role: str | None = None,
    ) -> Optional[DraftPackage]:
        enemy_names = build_enemy_team_names(player_to_team, player_to_champ, our_team)
        return self.build_draft_package(my_champion, enemy_names, role=role)

    def build_lane_matchup_package(
        self,
        my_champion: Any,
        enemy_champion: Any,
        *,
        role: str | None = None,
    ) -> Optional[dict[str, Any]]:
        if not self.knowledge:
            return None
        return self.knowledge.get_lane_matchup_insight(my_champion, enemy_champion, role=role)

    def economy_signals(
        self,
        *,
        game_time: float,
        creep_score: int,
        ward_score: float,
        hardcore_enabled: bool,
    ) -> list[EconomySignal]:
        return analyze_economy(
            game_time=game_time,
            creep_score=creep_score,
            ward_score=ward_score,
            hardcore_enabled=hardcore_enabled,
        )

    def classify_enemy_itemization(self, item_ids: list[int]) -> dict[str, list[str]]:
        if not self.knowledge:
            return {
                "armor": [],
                "magic_resist": [],
                "anti_heal": [],
                "armor_pen": [],
                "magic_pen": [],
                "tenacity": [],
            }
        return self.knowledge.classify_enemy_itemization(item_ids)

    def analyze_event(
        self,
        event: dict[str, Any],
        *,
        active_player_name: str | None,
        player_to_team: dict[str, str],
        player_to_champ: dict[str, str],
        our_team: str,
        voice,
        ally_drags: int,
        enemy_drags: int,
        map_pve_name,
    ) -> EventAnalysis:
        name = str(event.get("EventName") or "")
        if name == "ChampionKill":
            return analyze_champion_kill(
                event,
                active_player_name=active_player_name,
                player_to_team=player_to_team,
                player_to_champ=player_to_champ,
                our_team=our_team,
                voice=voice,
                map_pve_name=map_pve_name,
            )
        if name == "FirstBlood":
            return analyze_first_blood(voice)
        if name == "Multikill":
            return analyze_multikill(event, active_player_name=active_player_name, voice=voice)
        if name in {"DragonKill", "BaronKill", "HordeKill", "HeraldKill"}:
            return analyze_objective_event(
                event,
                player_to_team=player_to_team,
                our_team=our_team,
                voice=voice,
                ally_drags=ally_drags,
                enemy_drags=enemy_drags,
            )
        if name in {"TurretKilled", "InhibKilled"}:
            return analyze_structure_event(
                event,
                player_to_team=player_to_team,
                our_team=our_team,
                voice=voice,
            )
        return EventAnalysis()

    def _resolve_duo_synergy(
        self,
        my_champion: Any,
        allies: list[dict[str, Any]],
        role: str | None,
    ) -> Optional[dict[str, Any]]:
        if not self.knowledge:
            return None

        normalized_role = self.knowledge._normalize_role(role or "")
        if normalized_role not in {"bottom", "support"}:
            return None

        counterpart_role = "support" if normalized_role == "bottom" else "bottom"
        counterpart = next(
            (
                ally for ally in allies
                if self.knowledge._normalize_role(ally.get("role")) == counterpart_role
                and ally.get("champion")
            ),
            None,
        )
        if not counterpart:
            return None
        return self.knowledge.get_duo_synergy(my_champion, counterpart.get("champion"))

    def _resolve_jungle_synergy(
        self,
        my_champion: Any,
        allies: list[dict[str, Any]],
        role: str | None,
    ) -> Optional[dict[str, Any]]:
        if not self.knowledge:
            return None

        normalized_role = self.knowledge._normalize_role(role or "")
        jungle_ally = next(
            (
                ally for ally in allies
                if self.knowledge._normalize_role(ally.get("role")) == "jungle"
                and ally.get("champion")
            ),
            None,
        )

        if normalized_role == "jungle":
            lane_priority = ("mid", "top", "bottom", "support")
            for lane_role in lane_priority:
                lane_ally = next(
                    (
                        ally for ally in allies
                        if self.knowledge._normalize_role(ally.get("role")) == lane_role
                        and ally.get("champion")
                    ),
                    None,
                )
                if not lane_ally:
                    continue
                synergy = self.knowledge.get_jungle_lane_synergy(my_champion, lane_ally.get("champion"))
                if synergy:
                    return synergy
            return None

        if not jungle_ally:
            return None
        return self.knowledge.get_jungle_lane_synergy(jungle_ally.get("champion"), my_champion)
