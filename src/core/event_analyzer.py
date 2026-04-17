from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


def _clean_name(value: Any) -> str:
    return str(value or "").split("#")[0].strip()


@dataclass(slots=True)
class EventCall:
    text: str
    event_type: str
    category: str
    objective_only: bool = False
    importance: float = 0.65
    metadata: dict[str, Any] = field(default_factory=dict)
    memory_entry: dict[str, str] | None = None


@dataclass(slots=True)
class EventAnalysis:
    calls: list[EventCall] = field(default_factory=list)
    stat_updates: dict[str, Any] = field(default_factory=dict)


def analyze_champion_kill(
    event: dict[str, Any],
    *,
    active_player_name: str | None,
    player_to_team: dict[str, str],
    player_to_champ: dict[str, str],
    our_team: str,
    voice,
    map_pve_name,
) -> EventAnalysis:
    killer = _clean_name(event.get("KillerName"))
    victim = _clean_name(event.get("VictimName"))

    analysis = EventAnalysis()
    if killer == active_player_name:
        analysis.calls.append(
            EventCall(
                voice.self_kill(victim),
                "positive",
                "self_kill",
                importance=0.88,
                metadata={"impact": "snowball", "priority": "high", "subject": victim},
                memory_entry={"title": "Abate convertido", "note": f"Tu puniu {victim} e abriu janela de recurso no mapa.", "tone": "positive"},
            )
        )
        return analysis

    if victim == active_player_name:
        if not killer or killer not in player_to_champ:
            analysis.calls.append(
                EventCall(
                    voice.self_death_pve(),
                    "negative",
                    "self_death",
                    importance=0.94,
                    metadata={"impact": "throw", "priority": "critical", "subject": "pve"},
                    memory_entry={"title": "Morte gratuita", "note": "Tu morreu para o mapa e entregou tempo sem forçar nada em troca.", "tone": "negative"},
                )
            )
        else:
            analysis.calls.append(
                EventCall(
                    voice.self_death_enemy(killer),
                    "negative",
                    "self_death",
                    importance=0.96,
                    metadata={"impact": "throw", "priority": "critical", "subject": killer},
                    memory_entry={"title": "Janela entregue", "note": f"Tua morte para {killer} custou pressão e abriu mapa para o inimigo.", "tone": "negative"},
                )
            )
        return analysis

    if not killer or not victim:
        return analysis

    is_victim_ally = player_to_team.get(victim) == our_team
    if killer not in player_to_champ:
        pve = map_pve_name(killer)
        if is_victim_ally:
            analysis.calls.append(EventCall(voice.ally_pve_death(victim, pve), "negative", "ally_death", importance=0.74, metadata={"impact": "tempo perdido", "priority": "medium", "subject": victim}))
        else:
            analysis.calls.append(EventCall(voice.enemy_pve_death(victim, pve), "positive", "enemy_death", importance=0.76, metadata={"impact": "janela de mapa", "priority": "medium", "subject": victim}))
        return analysis

    if is_victim_ally:
        analysis.calls.append(EventCall(voice.ally_death(victim, killer), "negative", "ally_death", importance=0.78, metadata={"impact": "fight perdida", "priority": "medium", "subject": victim}))
    else:
        analysis.calls.append(EventCall(voice.enemy_death(killer, victim), "positive", "enemy_death", importance=0.8, metadata={"impact": "fight ganha", "priority": "medium", "subject": victim}))
    return analysis


def analyze_first_blood(voice) -> EventAnalysis:
    return EventAnalysis(calls=[EventCall(voice.first_blood(), "positive", "first_blood", importance=0.84, metadata={"impact": "ritmo cedo", "priority": "high"})])


def analyze_multikill(event: dict[str, Any], *, active_player_name: str | None, voice) -> EventAnalysis:
    killer = _clean_name(event.get("KillerName"))
    kill_streak = event.get("KillStreak", 2)

    if killer == active_player_name:
        return EventAnalysis(calls=[EventCall(voice.self_multikill(kill_streak), "positive", "multikill", importance=0.92, metadata={"impact": "fight decisiva", "priority": "high", "streak": kill_streak})])
    if kill_streak >= 2:
        return EventAnalysis(calls=[EventCall(voice.enemy_multikill(killer, kill_streak), "negative", "multikill", importance=0.93, metadata={"impact": "fight colapsou", "priority": "high", "streak": kill_streak, "subject": killer})])
    return EventAnalysis()


def analyze_objective_event(
    event: dict[str, Any],
    *,
    player_to_team: dict[str, str],
    our_team: str,
    voice,
    ally_drags: int,
    enemy_drags: int,
) -> EventAnalysis:
    name = str(event.get("EventName") or "")
    killer = _clean_name(event.get("KillerName"))
    is_ally = player_to_team.get(killer) == our_team
    event_type = "positive" if is_ally else "negative"
    analysis = EventAnalysis()

    if name == "DragonKill":
        raw_dragon = str(event.get("DragonType", "Dragão")).replace("Dragon", "")
        dragon_map = {
            "Fire": "Infernal",
            "Earth": "da Montanha",
            "Water": "do Oceano",
            "Air": "das Nuvens",
            "Hextech": "Hextec",
            "Chemtech": "Quimtec",
            "Elder": "Ancião",
        }
        dragon_pt = dragon_map.get(raw_dragon, raw_dragon)
        next_ally_drags = ally_drags + (1 if is_ally else 0)
        next_enemy_drags = enemy_drags + (0 if is_ally else 1)
        analysis.stat_updates = {
            "ally_drags": next_ally_drags,
            "enemy_drags": next_enemy_drags,
        }
        if dragon_pt == "Ancião":
            analysis.calls.append(EventCall(voice.elder_dragon(is_ally), event_type, "dragon", objective_only=True, importance=0.98, metadata={"impact": "elder", "priority": "critical", "objective": dragon_pt}))
        else:
            total_drags = next_ally_drags if is_ally else next_enemy_drags
            analysis.calls.append(
                EventCall(
                    voice.dragon_control(dragon_pt, is_ally, total_drags, killer),
                    event_type,
                    "dragon",
                    objective_only=True,
                    importance=0.9 if total_drags >= 3 else 0.82,
                    metadata={"impact": "soul_pressure" if total_drags >= 3 else "objective", "priority": "high" if total_drags >= 3 else "medium", "objective": dragon_pt, "stack": total_drags},
                )
            )
        return analysis

    objective_map = {
        "BaronKill": ("baron", voice.baron_taken),
        "HordeKill": ("horde", voice.horde_taken),
        "HeraldKill": ("herald", voice.herald_taken),
    }
    category, renderer = objective_map.get(name, (None, None))
    if category and renderer:
        importance = 0.94 if category == "baron" else 0.82
        priority = "critical" if category == "baron" else "medium"
        analysis.calls.append(EventCall(renderer(killer, is_ally), event_type, category, objective_only=True, importance=importance, metadata={"impact": "objective", "priority": priority, "objective": category}))
    return analysis


def analyze_structure_event(
    event: dict[str, Any],
    *,
    player_to_team: dict[str, str],
    our_team: str,
    voice,
) -> EventAnalysis:
    name = str(event.get("EventName") or "")
    killer = _clean_name(event.get("KillerName"))
    analysis = EventAnalysis()

    if name == "TurretKilled":
        if killer and "Turret" not in killer and "Minion" not in killer:
            is_ally = player_to_team.get(killer) == our_team
            analysis.calls.append(EventCall(voice.turret_taken(killer, is_ally), "positive" if is_ally else "negative", "turret", importance=0.78, metadata={"impact": "map_open", "priority": "medium", "subject": killer}))
        else:
            analysis.calls.append(EventCall(voice.neutral_turret_taken(), "negative", "turret", importance=0.7, metadata={"impact": "map_shift", "priority": "medium"}))
        return analysis

    if name == "InhibKilled":
        is_ally = player_to_team.get(killer) == our_team
        analysis.calls.append(EventCall(voice.inhibitor_taken(killer, is_ally), "positive" if is_ally else "negative", "inhibitor", importance=0.95, metadata={"impact": "base_breach", "priority": "critical", "subject": killer}))
    return analysis
