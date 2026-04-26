from __future__ import annotations

import json
import os
import re
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import requests
from core.app_paths import resource_path


_DD_BASE_URL = "https://ddragon.leagueoflegends.com"
_NORMALIZE_RE = re.compile(r"[^a-z0-9]+")
_REQUEST_TIMEOUT = 12
_OVERRIDES_PATH = resource_path("data", "league_knowledge", "curated_overrides.json")

_ENCHANTERS = {
    "Bard", "Janna", "Karma", "Lulu", "Milio", "Nami", "Renata Glasc",
    "Seraphine", "Sona", "Soraka", "Taric", "Yuumi", "Zilean", "Ivern",
}
_ENGAGE_SUPPORTS = {
    "Alistar", "Amumu", "Blitzcrank", "Leona", "Maokai", "Nautilus",
    "Rakan", "Rell", "Thresh",
}
_POKE_SUPPORTS = {"Brand", "Karma", "Lux", "Seraphine", "Vel'Koz", "Xerath", "Zyra"}
_AGGRESSIVE_BOT_CARRIES = {
    "Ashe", "Caitlyn", "Draven", "Kalista", "Lucian", "Miss Fortune",
    "Samira", "Varus",
}
_HYPER_SCALING_BOT_CARRIES = {
    "Aphelios", "Jinx", "Kog'Maw", "Sivir", "Twitch", "Vayne", "Zeri",
}
_CONTROL_MAGES = {
    "Anivia", "Azir", "Cassiopeia", "Hwei", "Lissandra", "Lux", "Malzahar",
    "Orianna", "Ryze", "Syndra", "Taliyah", "Twisted Fate", "Veigar",
    "Vel'Koz", "Viktor", "Xerath", "Zoe",
}
_JUGGERNAUTS = {
    "Aatrox", "Darius", "Dr. Mundo", "Garen", "Illaoi", "Mordekaiser",
    "Nasus", "Olaf", "Sett", "Trundle", "Urgot", "Volibear",
}
_SKIRMISHERS = {
    "Bel'Veth", "Camille", "Fiora", "Gwen", "Irelia", "Jax", "Master Yi",
    "Riven", "Sylas", "Tryndamere", "Viego", "Yasuo", "Yone",
}
_SUSTAIN_CHAMPS = {
    "Aatrox", "Briar", "Dr. Mundo", "Fiddlesticks", "Illaoi", "Olaf",
    "Samira", "Soraka", "Swain", "Sylas", "Vladimir", "Warwick", "Yuumi",
}
_HARD_CC_CHAMPS = {
    "Amumu", "Ashe", "Blitzcrank", "Leona", "Lissandra", "Maokai",
    "Morgana", "Nautilus", "Rell", "Sejuani", "Thresh", "Varus", "Zac",
}
_ROLE_BAN_POOL = {
    "top": [
        "Aatrox", "Camille", "Darius", "Fiora", "Gwen", "Illaoi", "Jax",
        "Kennen", "Malphite", "Mordekaiser", "Olaf", "Ornn", "Renekton",
        "Riven", "Sett", "Volibear", "Yone",
    ],
    "jungle": [
        "Bel'Veth", "Briar", "Elise", "Jarvan IV", "Kha'Zix", "Lee Sin",
        "Nocturne", "Rengar", "Sejuani", "Skarner", "Viego", "Vi",
        "Wukong", "Xin Zhao", "Zac",
    ],
    "mid": [
        "Ahri", "Akali", "Azir", "Hwei", "LeBlanc", "Lissandra", "Orianna",
        "Syndra", "Sylas", "Taliyah", "Viktor", "Yasuo", "Yone", "Zed",
    ],
    "bottom": [
        "Ashe", "Caitlyn", "Draven", "Jhin", "Jinx", "Kai'Sa", "Kalista",
        "Lucian", "Miss Fortune", "Samira", "Tristana", "Varus", "Xayah",
        "Zeri",
    ],
    "support": [
        "Bard", "Blitzcrank", "Leona", "Lulu", "Milio", "Morgana",
        "Nami", "Nautilus", "Pyke", "Rakan", "Rell", "Thresh",
        "Yuumi", "Zyra",
    ],
}

_ARCHETYPE_POWER_SPIKES = {
    "marksman": (
        "primeiro item completo",
        "dois itens para fight mais longa",
        "tres itens quando teu DPS vira condicao de vitoria",
    ),
    "assassin": (
        "nivel 6 para all-in limpo",
        "primeiro item de burst ou letalidade",
        "dois itens quando pickoff vira morte certa",
    ),
    "control_mage": (
        "nivel 6 com wave control na mao",
        "primeiro item de mana e pressao",
        "dois itens quando teu zoneamento decide luta",
    ),
    "burst_mage": (
        "nivel 6",
        "primeiro item de burst",
        "dois itens para explodir alvo fora de posicao",
    ),
    "skirmisher": (
        "nivel 3 para troca longa",
        "nivel 6 para all-in ou dive",
        "um a dois itens quando side lane abre",
    ),
    "juggernaut": (
        "nivel 6",
        "primeiro item de luta longa",
        "dois itens quando teu side pressure fica serio",
    ),
    "bruiser": (
        "nivel 3",
        "nivel 6",
        "primeiro item pra dominar troca estendida",
    ),
    "tank": (
        "primeiro item defensivo",
        "nivel 6 para iniciar com mais autoridade",
        "dois itens quando tu vira front line de verdade",
    ),
    "engage_support": (
        "nivel 2",
        "nivel 6",
        "bota e primeiro item de engage",
    ),
    "enchanter": (
        "nivel 6",
        "primeiro item utilitario",
        "dois itens quando teu peel ou buff muda a fight",
    ),
    "poke_support": (
        "primeiro recall",
        "nivel 6",
        "primeiro item de poke ou queimadura",
    ),
}

# Maps archetype → need_type → list of specific item names (priority order)
_ARCHETYPE_ITEM_MAP = {
    "marksman": {
        "anti_heal": ["Lembrete Mortal"],
        "armor_pen": ["Lembranças do Lorde Dominik"],
        "magic_pen": [],
        "defensive": ["Anjo Guardião", "Dança da Morte"],
        "tenacity": ["Botas de Mercúrio"],
        "anti_burst": ["Anjo Guardião"],
        "anti_shield": ["Lâmina do Rei Destruído"],
        "vs_tanks": ["Lembranças do Lorde Dominik", "Lâmina do Rei Destruído"],
    },
    "assassin": {
        "anti_heal": ["Chamado do Carrasco", "Chempunk"],
        "armor_pen": ["Rencor de Serylda", "Youmuu"],
        "magic_pen": [],
        "defensive": ["Limiar da Morte", "Anjo Guardião"],
        "tenacity": ["Botas de Mercúrio"],
        "anti_burst": ["Limiar da Morte"],
        "vs_tanks": ["Lâmina do Rei Destruído", "Rencor de Serylda"],
    },
    "control_mage": {
        "anti_heal": ["Orbe do Esquecimento", "Morellonomicon"],
        "armor_pen": [],
        "magic_pen": ["Cajado do Vazio"],
        "defensive": ["Ampulheta de Zhonya", "Coroa da Rainha Destruída"],
        "tenacity": ["Botas de Mercúrio"],
        "anti_burst": ["Ampulheta de Zhonya", "Escudo de Banshee"],
        "vs_tanks": ["Cajado do Vazio", "Tormento de Liandry"],
    },
    "burst_mage": {
        "anti_heal": ["Orbe do Esquecimento", "Morellonomicon"],
        "armor_pen": [],
        "magic_pen": ["Cajado do Vazio"],
        "defensive": ["Ampulheta de Zhonya"],
        "tenacity": ["Botas de Mercúrio"],
        "anti_burst": ["Ampulheta de Zhonya", "Escudo de Banshee"],
        "vs_tanks": ["Cajado do Vazio"],
    },
    "skirmisher": {
        "anti_heal": ["Chamado do Carrasco", "Chempunk"],
        "armor_pen": ["Rencor de Serylda"],
        "magic_pen": [],
        "defensive": ["Dança da Morte", "Anjo Guardião"],
        "tenacity": ["Botas de Mercúrio"],
        "anti_burst": ["Limiar da Morte", "Anjo Guardião"],
        "vs_tanks": ["Lâmina do Rei Destruído", "Rencor de Serylda"],
    },
    "juggernaut": {
        "anti_heal": ["Vestimenta de Espinhos", "Chamado do Carrasco"],
        "armor_pen": ["Rencor de Serylda", "Machadinha Negra"],
        "magic_pen": [],
        "defensive": ["Placa do Espírito", "Manopla do Nascimento Estéril"],
        "tenacity": ["Botas de Mercúrio"],
        "anti_burst": ["Manopla do Nascimento Estéril"],
        "vs_tanks": ["Machadinha Negra", "Rencor de Serylda"],
    },
    "bruiser": {
        "anti_heal": ["Chamado do Carrasco", "Chempunk"],
        "armor_pen": ["Rencor de Serylda", "Machadinha Negra"],
        "magic_pen": [],
        "defensive": ["Dança da Morte", "Anjo Guardião"],
        "tenacity": ["Botas de Mercúrio"],
        "anti_burst": ["Anjo Guardião", "Limiar da Morte"],
        "vs_tanks": ["Lâmina do Rei Destruído", "Machadinha Negra"],
    },
    "tank": {
        "anti_heal": ["Vestimenta de Espinhos"],
        "armor_pen": [],
        "magic_pen": [],
        "defensive": ["Placa de Pedra", "Coração Congelado"],
        "tenacity": ["Botas de Mercúrio"],
        "anti_burst": ["Placa de Pedra"],
        "vs_tanks": [],
    },
    "engage_support": {
        "anti_heal": ["Vestimenta de Espinhos"],
        "armor_pen": [],
        "magic_pen": [],
        "defensive": ["Convergência de Zeke", "Juramento do Cavaleiro"],
        "tenacity": ["Botas de Mercúrio"],
        "anti_burst": ["Juramento do Cavaleiro"],
        "vs_tanks": [],
    },
    "enchanter": {
        "anti_heal": ["Orbe do Esquecimento"],
        "armor_pen": [],
        "magic_pen": [],
        "defensive": ["Ampulheta de Zhonya", "Redenção"],
        "tenacity": ["Botas de Mercúrio"],
        "anti_burst": ["Ampulheta de Zhonya"],
        "vs_tanks": [],
    },
    "poke_support": {
        "anti_heal": ["Orbe do Esquecimento", "Morellonomicon"],
        "armor_pen": [],
        "magic_pen": ["Cajado do Vazio"],
        "defensive": ["Ampulheta de Zhonya"],
        "tenacity": ["Botas de Mercúrio"],
        "anti_burst": ["Ampulheta de Zhonya"],
        "vs_tanks": ["Tormento de Liandry"],
    },
}

# Champion-specific item overrides for cases where archetype defaults are wrong
_CHAMPION_ITEM_OVERRIDES = {
    # AP assassins that need magic pen, not armor pen
    "Akali": {"magic_pen": ["Cajado do Vazio"], "anti_heal": ["Orbe do Esquecimento", "Morellonomicon"], "defensive": ["Ampulheta de Zhonya"]},
    "Katarina": {"magic_pen": ["Cajado do Vazio"], "anti_heal": ["Orbe do Esquecimento"], "defensive": ["Ampulheta de Zhonya"]},
    "Evelynn": {"magic_pen": ["Cajado do Vazio"], "anti_heal": ["Orbe do Esquecimento"], "defensive": ["Ampulheta de Zhonya"]},
    "Fizz": {"magic_pen": ["Cajado do Vazio"], "anti_heal": ["Orbe do Esquecimento"], "defensive": ["Ampulheta de Zhonya"]},
    "Diana": {"magic_pen": ["Cajado do Vazio"], "anti_heal": ["Orbe do Esquecimento"], "defensive": ["Ampulheta de Zhonya"]},
    "Elise": {"magic_pen": ["Cajado do Vazio"], "anti_heal": ["Orbe do Esquecimento"], "defensive": ["Ampulheta de Zhonya"]},
    "Ekko": {"magic_pen": ["Cajado do Vazio"], "anti_heal": ["Orbe do Esquecimento"], "defensive": ["Ampulheta de Zhonya"]},
    "Nidalee": {"magic_pen": ["Cajado do Vazio"], "anti_heal": ["Orbe do Esquecimento"], "defensive": ["Ampulheta de Zhonya"]},
    "LeBlanc": {"magic_pen": ["Cajado do Vazio"], "anti_heal": ["Orbe do Esquecimento"], "defensive": ["Ampulheta de Zhonya", "Escudo de Banshee"]},
    # Hybrid fighters
    "Mordekaiser": {"magic_pen": ["Cajado do Vazio"], "anti_heal": ["Orbe do Esquecimento"], "vs_tanks": ["Cajado do Vazio", "Tormento de Liandry"]},
    "Rumble": {"magic_pen": ["Cajado do Vazio"], "anti_heal": ["Orbe do Esquecimento"], "vs_tanks": ["Cajado do Vazio"]},
    # Kayn: depends on form but base AD
    "Kayn": {"anti_heal": ["Chamado do Carrasco"], "defensive": ["Dança da Morte", "Anjo Guardião"]},
    # Specific QSS champions
    "Malzahar": {},  # handled in counter logic
    "Skarner": {},
}


_MATCHUP_RULES = {
    ("control_mage", "assassin"): {
        "verdict": "skill",
        "plan": "abusa alcance cedo, guarda recurso pro all-in e nao entrega flank gratis",
        "danger": "nivel 6 e janela sem spell defensiva",
    },
    ("assassin", "control_mage"): {
        "verdict": "explosivo",
        "plan": "joga escondendo entrada, corta visao e acelera quando o mago gastar ferramenta-chave",
        "danger": "poke e push cedo demais na wave",
    },
    ("marksman", "engage_support"): {
        "verdict": "perigoso",
        "plan": "usa tropa como escudo, respeita nivel 2 e so troca quando a wave estiver curta",
        "danger": "engage reto com wave grande ou sem flash",
    },
    ("engage_support", "marksman"): {
        "verdict": "favoravel se entrares bem",
        "plan": "joga por janela de engage, trava wave e cobra summoner mal gasto",
        "danger": "poke gratuito antes de achar o engage",
    },
    ("juggernaut", "marksman"): {
        "verdict": "all-in ou nada",
        "plan": "encurta a lane, controla mato e joga por entrada curta e decisiva",
        "danger": "tomar kite de graca com wave longa",
    },
    ("marksman", "juggernaut"): {
        "verdict": "bom se tu kitear direito",
        "plan": "mantem espacamento, pressiona wave e nao entrega parede ou brush de flanco",
        "danger": "troca longa perto demais",
    },
    ("tank", "juggernaut"): {
        "verdict": "paciencia",
        "plan": "segura wave, joga por recurso e prepara teamfight em vez de side egoista",
        "danger": "troca longa sem item",
    },
    ("skirmisher", "tank"): {
        "verdict": "escalavel",
        "plan": "pune janela curta cedo e depois joga por side e itemizacao certa",
        "danger": "entrar em luta longa quando o tanque ja fechou defesa",
    },
}


def _normalize_name(value: Any) -> str:
    text = str(value or "").lower()
    text = text.replace("'", "").replace(".", "").replace("&", " and ")
    return _NORMALIZE_RE.sub("", text)


def _first_sentence(value: str) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", "", text)
    parts = re.split(r"(?<=[.!?])\s+", text)
    return parts[0].strip() if parts else text


def _default_cache_dir() -> Path:
    appdata = os.getenv("LOCALAPPDATA") or os.getenv("APPDATA")
    if appdata:
        return Path(appdata).expanduser() / "Coacher" / "league_knowledge"
    return Path.home() / ".coacher" / "league_knowledge"


def _read_json(path: Path) -> Optional[dict[str, Any]]:
    try:
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(base, dict):
        return dict(override or {})
    if not isinstance(override, dict):
        return dict(base)

    merged = dict(base)
    for key, value in override.items():
        current = merged.get(key)
        if isinstance(current, dict) and isinstance(value, dict):
            merged[key] = _deep_merge(current, value)
        else:
            merged[key] = value
    return merged


@dataclass(slots=True)
class ChampionKnowledge:
    id: int
    key: str
    name: str
    title: str
    blurb: str
    tags: tuple[str, ...]
    partype: str
    info: dict[str, Any]
    stats: dict[str, Any]
    archetype: str
    power_spikes: tuple[str, ...]
    ally_tips: tuple[str, ...]
    enemy_tips: tuple[str, ...]


@dataclass(slots=True)
class ItemKnowledge:
    id: int
    name: str
    plaintext: str
    description: str
    tags: tuple[str, ...]
    stats: dict[str, Any]
    coach_tags: tuple[str, ...]


@dataclass(slots=True)
class RoleProfile:
    champion: str
    role: str
    opening_plan: str
    lane_plan: str
    first_reset_focus: str
    mid_game_job: str
    situational_items: tuple[str, ...]


@dataclass(slots=True)
class PickRecommendation:
    champion: str
    role: str
    focus: str
    context: str
    window: str
    score: float
    reasons: tuple[str, ...]
    familiarity: str
    comp_style: str
    build_focus: tuple[str, ...]
    power_spikes: tuple[str, ...]
    lane_plan_summary: str
    lane_win_condition: str
    lane_fail_condition: str


@dataclass(slots=True)
class BanRecommendation:
    champion: str
    role: str
    stage: str
    focus: str
    context: str
    window: str
    score: float
    reasons: tuple[str, ...]


class LeagueKnowledgeBase:
    def __init__(
        self,
        locale: str = "pt_BR",
        cache_dir: str | Path | None = None,
        preload: bool = True,
        remote_feed_url: str | None = None,
        remote_feed_ttl_hours: float | None = None,
    ):
        self.locale = locale
        self.cache_dir = Path(cache_dir).expanduser() if cache_dir else _default_cache_dir()
        self.remote_feed_url = (remote_feed_url or os.getenv("COACHER_KNOWLEDGE_FEED_URL") or "").strip()
        ttl_value = remote_feed_ttl_hours
        if ttl_value is None:
            try:
                ttl_value = float(os.getenv("COACHER_KNOWLEDGE_FEED_TTL_HOURS", "6"))
            except ValueError:
                ttl_value = 6.0
        self.remote_feed_ttl_seconds = max(0.0, float(ttl_value) * 3600.0)
        self._lock = threading.RLock()
        self._patch: Optional[str] = None
        self._champions_by_id: dict[int, dict[str, Any]] = {}
        self._champions_by_name: dict[str, dict[str, Any]] = {}
        self._items_by_id: dict[int, dict[str, Any]] = {}
        self._items_by_name: dict[str, dict[str, Any]] = {}
        self._champion_cache: dict[str, ChampionKnowledge] = {}
        self._item_cache: dict[int, ItemKnowledge] = {}
        self._details_cache: dict[str, dict[str, Any]] = {}
        self._overrides = self._load_overrides()

        if preload:
            threading.Thread(target=self.ensure_static_data, daemon=True).start()

    @property
    def patch(self) -> Optional[str]:
        self.ensure_static_data()
        return self._patch

    def get_champion_name(self, champion_id: int) -> str:
        champion = self.get_champion(champion_id)
        return champion.name if champion else f"Campeão {champion_id}"

    def get_champion(self, identifier: Any) -> Optional[ChampionKnowledge]:
        self.ensure_static_data()
        raw = self._resolve_champion(identifier)
        if raw is None:
            return None

        cache_key = raw["key"]
        with self._lock:
            if cache_key in self._champion_cache:
                return self._champion_cache[cache_key]

        detail = self._load_champion_detail(cache_key)
        champion = ChampionKnowledge(
            id=int(raw["id"]),
            key=cache_key,
            name=raw["name"],
            title=raw.get("title", ""),
            blurb=raw.get("blurb", ""),
            tags=tuple(raw.get("tags", [])),
            partype=raw.get("partype", ""),
            info=dict(raw.get("info", {})),
            stats=dict(raw.get("stats", {})),
            archetype=self._infer_archetype(raw),
            power_spikes=self._power_spikes_for(raw),
            ally_tips=tuple(detail.get("allytips", [])) if detail else (),
            enemy_tips=tuple(detail.get("enemytips", [])) if detail else (),
        )
        with self._lock:
            self._champion_cache[cache_key] = champion
        return champion

    def get_item(self, identifier: Any) -> Optional[ItemKnowledge]:
        self.ensure_static_data()
        raw = self._resolve_item(identifier)
        if raw is None:
            return None

        item_id = int(raw["id"])
        with self._lock:
            if item_id in self._item_cache:
                return self._item_cache[item_id]

        item = ItemKnowledge(
            id=item_id,
            name=raw["name"],
            plaintext=raw.get("plaintext", ""),
            description=raw.get("description", ""),
            tags=tuple(raw.get("tags", [])),
            stats=dict(raw.get("stats", {})),
            coach_tags=self._coach_tags_for_item(raw),
        )
        with self._lock:
            self._item_cache[item_id] = item
        return item

    def get_lane_matchup_insight(self, my_champion: Any, enemy_champion: Any, role: str | None = None) -> Optional[dict[str, Any]]:
        mine = self.get_champion(my_champion)
        enemy = self.get_champion(enemy_champion)
        if not mine or not enemy:
            return None
        role_profile = self.get_role_profile(mine.name, role)

        override = self._matchup_override(mine.name, enemy.name, role)
        if override:
            spike_race = override.get("spike_race") or f"Teu primeiro pico forte vem em {mine.power_spikes[0]}; o dele costuma aparecer em {enemy.power_spikes[0]}."
            return {
                "my_champion": mine.name,
                "enemy_champion": enemy.name,
                "role": role or "",
                "verdict": override.get("verdict", "skill"),
                "plan": override.get("plan", ""),
                "danger": override.get("danger", ""),
                "spike_race": spike_race,
                "lane_plan": role_profile.lane_plan if role_profile else "",
                "lane_windows": list(override.get("lane_windows") or self._matchup_lane_windows(mine, enemy, role)),
                "first_reset_focus": role_profile.first_reset_focus if role_profile else "",
                "first_item_plan": override.get("first_item_plan") or self._default_first_item_plan(mine, self._normalize_role(role or ""), self._build_focus(mine, self._threat_counts([enemy]))),
                "recommended_setup": override.get("recommended_setup") or self._recommended_setup(mine, enemy, role),
                "lane_win_condition": override.get("lane_win_condition") or self._lane_win_condition(mine, enemy, role),
                "lane_fail_condition": override.get("lane_fail_condition") or self._lane_fail_condition(mine, enemy, role),
            }

        rule = _MATCHUP_RULES.get((mine.archetype, enemy.archetype), {})
        my_tip = _first_sentence(mine.ally_tips[0]) if mine.ally_tips else ""
        enemy_tip = _first_sentence(enemy.enemy_tips[0]) if enemy.enemy_tips else ""

        attack_range = mine.stats.get("attackrange", 0) - enemy.stats.get("attackrange", 0)
        verdict = rule.get("verdict")
        if not verdict:
            if attack_range >= 125:
                verdict = "pressionavel"
            elif attack_range <= -125:
                verdict = "delicado"
            else:
                verdict = "skill"

        plan = rule.get("plan") or my_tip or f"joga a lane de {mine.name} em cima do teu alcance, da tua wave e do teu primeiro spike"
        danger = rule.get("danger") or enemy_tip or f"respeita a janela de entrada de {enemy.name} e nao da espaco sem visao"

        return {
            "my_champion": mine.name,
            "enemy_champion": enemy.name,
            "role": role or "",
            "verdict": verdict,
            "plan": plan,
            "danger": danger,
            "spike_race": f"Teu primeiro pico forte vem em {mine.power_spikes[0]}; o dele costuma aparecer em {enemy.power_spikes[0]}.",
            "lane_plan": role_profile.lane_plan if role_profile else "",
            "lane_windows": self._matchup_lane_windows(mine, enemy, role),
            "first_reset_focus": role_profile.first_reset_focus if role_profile else "",
            "first_item_plan": self._default_first_item_plan(mine, self._normalize_role(role or ""), self._build_focus(mine, self._threat_counts([enemy]))),
            "recommended_setup": self._recommended_setup(mine, enemy, role),
            "lane_win_condition": self._lane_win_condition(mine, enemy, role),
            "lane_fail_condition": self._lane_fail_condition(mine, enemy, role),
        }

    def get_draft_guidance(
        self,
        my_champion: Any,
        enemy_team: list[Any],
        role: str | None = None,
        allies: list[dict[str, Any]] | None = None,
    ) -> Optional[dict[str, Any]]:
        mine = self.get_champion(my_champion)
        if not mine:
            return None

        enemy_profiles = [self.get_champion(enemy) for enemy in enemy_team]
        enemy_profiles = [champ for champ in enemy_profiles if champ]
        threats = self._threat_counts(enemy_profiles)
        comp_style = self._infer_comp_style(threats)
        build_focus = self._build_focus(mine, threats)
        power_spikes = list(self._power_spikes_for(mine))
        pressure_points = self._pressure_points(threats)
        role_profile = self.get_role_profile(mine.name, role)
        role_key = self._normalize_role(role or "")
        ally_profiles = self._allied_profiles(mine, allies or [])
        ally_threats = self._threat_counts(ally_profiles)
        ally_identity = self._infer_allied_comp_identity(ally_profiles, ally_threats)

        champion_override = self._champion_override(mine.name)
        if champion_override:
            override_spikes = champion_override.get("power_spikes") or []
            override_focus = champion_override.get("draft_build_focus") or []
            if override_spikes:
                power_spikes = list(override_spikes)
            if override_focus:
                build_focus = _merge_unique(override_focus, build_focus)

        return {
            "champion": mine.name,
            "archetype": mine.archetype,
            "power_spikes": power_spikes,
            "comp_style": comp_style,
            "pressure_points": pressure_points,
            "build_focus": build_focus,
            "opening_plan": role_profile.opening_plan if role_profile else "",
            "lane_plan": role_profile.lane_plan if role_profile else "",
            "lane_windows": self._default_lane_windows(mine, role_key),
            "first_reset_focus": role_profile.first_reset_focus if role_profile else "",
            "first_item_plan": self._default_first_item_plan(mine, role_key, build_focus),
            "reset_adjustment": self._draft_reset_adjustment(mine, threats, role_key),
            "map_plan_summary": self._draft_map_plan_summary(mine, threats, role_key, ally_identity=ally_identity),
            "fight_plan_summary": self._draft_fight_plan_summary(mine, threats, role_key, ally_identity=ally_identity),
            "team_plan_summary": self._draft_team_plan_summary(ally_identity, role_key),
            "ally_comp_identity": ally_identity,
            "mid_game_job": role_profile.mid_game_job if role_profile else "",
            "situational_items": list(role_profile.situational_items) if role_profile else [],
        }

    def get_role_profile(self, champion_name: Any, role: str | None = None) -> Optional[RoleProfile]:
        champion = self.get_champion(champion_name)
        if not champion:
            return None

        role_key = self._normalize_role(role or "")
        override = self._role_override(champion.name, role_key)
        opening_plan = override.get("opening_plan") or self._default_opening_plan(champion, role_key)
        lane_plan = override.get("lane_plan") or self._default_lane_plan(champion, role_key)
        first_reset_focus = override.get("first_reset_focus") or self._default_first_reset_focus(champion, role_key)
        mid_game_job = override.get("mid_game_job") or self._default_mid_game_job(champion, role_key)
        situational_items = tuple(override.get("situational_items") or self._default_situational_items(champion))

        return RoleProfile(
            champion=champion.name,
            role=role_key or "general",
            opening_plan=opening_plan,
            lane_plan=lane_plan,
            first_reset_focus=first_reset_focus,
            mid_game_job=mid_game_job,
            situational_items=situational_items,
        )

    def classify_enemy_itemization(self, item_ids: list[int]) -> dict[str, list[str]]:
        result = {
            "armor": [],
            "magic_resist": [],
            "anti_heal": [],
            "armor_pen": [],
            "magic_pen": [],
            "tenacity": [],
        }
        for item_id in item_ids:
            item = self.get_item(item_id)
            if not item:
                continue
            for coach_tag in item.coach_tags:
                if coach_tag in result:
                    result[coach_tag].append(item.name)
        return result

    def get_duo_synergy(self, first_champion: Any, second_champion: Any) -> Optional[dict[str, Any]]:
        first = self.get_champion(first_champion)
        second = self.get_champion(second_champion)
        if not first or not second:
            return None

        override = self._duo_synergy_override(first.name, second.name)
        if override:
            return {
                "label": override.get("label", "dupla forte"),
                "plan": override.get("plan", ""),
                "spike": override.get("spike", ""),
                "champions": [first.name, second.name],
            }

        return self._infer_duo_synergy(first, second)

    def get_jungle_lane_synergy(self, jungler: Any, laner: Any) -> Optional[dict[str, Any]]:
        jungle = self.get_champion(jungler)
        lane = self.get_champion(laner)
        if not jungle or not lane:
            return None

        override = self._jungle_lane_synergy_override(jungle.name, lane.name)
        if override:
            return {
                "label": override.get("label", "setup forte de gank"),
                "plan": override.get("plan", ""),
                "spike": override.get("spike", ""),
                "champions": [jungle.name, lane.name],
            }

        return self._infer_jungle_lane_synergy(jungle, lane)

    def recommend_counter_picks(
        self,
        enemy_team: list[Any],
        *,
        role: str | None = None,
        enemy_anchor: Any | None = None,
        allies: list[dict[str, Any]] | None = None,
        revealed_enemies: list[dict[str, Any]] | None = None,
        draft_window: dict[str, Any] | None = None,
        banned: list[Any] | None = None,
        main_champions: list[str] | None = None,
        preferred_pool: list[str] | None = None,
        prioritize_pool: bool = True,
        limit: int = 3,
    ) -> list[PickRecommendation]:
        enemy_profiles = [self.get_champion(enemy) for enemy in enemy_team]
        enemy_profiles = [champ for champ in enemy_profiles if champ]
        if not enemy_profiles:
            return []

        normalized_role = self._normalize_role(role or "")
        threats = self._threat_counts(enemy_profiles)
        comp_style = self._infer_comp_style(threats)
        candidate_names = self._draft_candidate_pool(normalized_role)
        banned_names = {_normalize_name(name) for name in (banned or [])}
        ally_names = {
            _normalize_name((ally or {}).get("champion"))
            for ally in (allies or [])
            if (ally or {}).get("champion")
        }
        enemy_names = [champ.name for champ in enemy_profiles]
        enemy_name_set = {_normalize_name(name) for name in enemy_names}
        pool_names = {
            _normalize_name(champion_name)
            for champion_name in (preferred_pool or [])
            if champion_name
        }
        main_names = {
            _normalize_name(champion_name)
            for champion_name in (main_champions or [])
            if champion_name
        }

        recommendations: list[PickRecommendation] = []
        for candidate_name in candidate_names:
            candidate = self.get_champion(candidate_name)
            if not candidate:
                continue

            normalized_candidate = _normalize_name(candidate.name)
            if (
                normalized_candidate in banned_names
                or normalized_candidate in ally_names
                or normalized_candidate in enemy_name_set
            ):
                continue

            score, reasons = self._score_pick_candidate(
                candidate,
                enemy_profiles,
                threats,
                role=normalized_role,
                allies=allies or [],
                revealed_enemies=revealed_enemies or [],
                draft_window=draft_window or {},
            )
            familiarity = "off_pool"
            if normalized_candidate in main_names:
                familiarity = "main"
                score += 14
                reasons = ["é um dos teus mains e continua forte nessa draft", *reasons]
            elif normalized_candidate in pool_names:
                familiarity = "pool"
                score += 8 if prioritize_pool else 3
                reasons = ["esta na tua pool preferida", *reasons]
            elif prioritize_pool and (main_names or pool_names):
                score -= 4
                reasons = [*reasons, "é resposta boa, mas foge do que tu mais joga"]
            if not reasons:
                reasons = ["resposta solida para a comp mostrada ate aqui"]
            score, reasons = self._adjust_pick_for_draft_window(
                score,
                reasons,
                role=normalized_role,
                familiarity=familiarity,
                draft_window=draft_window or {},
                enemy_anchor=enemy_anchor,
            )

            guidance = self.get_draft_guidance(candidate.name, enemy_names, role=normalized_role) or {}
            matchup_anchor = None
            if enemy_anchor:
                matchup_anchor = self.get_lane_matchup_insight(candidate.name, enemy_anchor, role=normalized_role) or {}
            recommendations.append(
                PickRecommendation(
                    champion=candidate.name,
                    role=normalized_role or "flex",
                    focus=self._classify_pick_focus(
                        reasons,
                        familiarity=familiarity,
                        role=normalized_role,
                    ),
                    context=self._classify_pick_context(
                        role=normalized_role,
                        revealed_enemies=revealed_enemies or [],
                        enemy_anchor=enemy_anchor,
                    ),
                    window=self._classify_pick_window(
                        draft_window=draft_window or {},
                        familiarity=familiarity,
                        enemy_anchor=enemy_anchor,
                        role=role,
                    ),
                    score=score,
                    reasons=tuple(reasons[:3]),
                    familiarity=familiarity,
                    comp_style=guidance.get("comp_style", comp_style),
                    build_focus=tuple(guidance.get("build_focus", [])[:2]),
                    power_spikes=tuple(guidance.get("power_spikes", [])[:2]),
                    lane_plan_summary=self._pick_lane_plan_summary(
                        candidate,
                        enemy_profiles,
                        role=normalized_role,
                        enemy_anchor=enemy_anchor,
                    ),
                    lane_win_condition=(matchup_anchor or {}).get("lane_win_condition", ""),
                    lane_fail_condition=(matchup_anchor or {}).get("lane_fail_condition", ""),
                )
            )

        recommendations.sort(key=lambda item: item.score, reverse=True)

        if prioritize_pool and recommendations and (main_names or pool_names):
            best = recommendations[0]
            preferred_candidates = [
                item for item in recommendations
                if item.familiarity in {"main", "pool"}
            ]
            if preferred_candidates:
                best_preferred = preferred_candidates[0]
                score_gap = best.score - best_preferred.score
                if best.familiarity == "off_pool" and score_gap <= 6:
                    recommendations.remove(best_preferred)
                    recommendations.insert(0, best_preferred)

        return recommendations[: max(1, limit)]

    def recommend_bans(
        self,
        enemy_team: list[Any],
        *,
        role: str | None = None,
        stage: str = "ban",
        current_pick: Any | None = None,
        revealed_enemies: list[dict[str, Any]] | None = None,
        draft_window: dict[str, Any] | None = None,
        main_champions: list[str] | None = None,
        preferred_pool: list[str] | None = None,
        banned: list[Any] | None = None,
        limit: int = 3,
    ) -> list[BanRecommendation]:
        normalized_role = self._normalize_role(role or "")
        stage_key = str(stage or "ban").strip().lower()
        enemy_profiles = [self.get_champion(enemy) for enemy in enemy_team]
        enemy_profiles = [champ for champ in enemy_profiles if champ]
        enemy_names = {_normalize_name(champ.name) for champ in enemy_profiles}
        banned_names = {_normalize_name(name) for name in (banned or [])}
        current = self.get_champion(current_pick) if current_pick else None
        current_name = _normalize_name(current.name) if current else ""
        preferred_profiles = [
            self.get_champion(champion)
            for champion in [*(main_champions or []), *(preferred_pool or [])]
        ]
        preferred_profiles = [champ for champ in preferred_profiles if champ]

        recommendations: list[BanRecommendation] = []
        for candidate_name in self._draft_ban_candidate_pool(normalized_role, enemy_profiles, current, revealed_enemies=revealed_enemies or []):
            candidate = self.get_champion(candidate_name)
            if not candidate:
                continue

            normalized_candidate = _normalize_name(candidate.name)
            if (
                normalized_candidate in banned_names
                or normalized_candidate in enemy_names
                or normalized_candidate == current_name
            ):
                continue

            score, reasons = self._score_ban_candidate(
                candidate,
                enemy_profiles,
                role=normalized_role,
                stage=stage,
                current_pick=current,
                revealed_enemies=revealed_enemies or [],
                draft_window=draft_window or {},
                preferred_pool=preferred_profiles,
            )
            score, reasons = self._adjust_ban_for_draft_window(
                score,
                reasons,
                role=normalized_role,
                current_pick=current,
                draft_window=draft_window or {},
            )
            if not reasons:
                continue

            recommendations.append(
                BanRecommendation(
                    champion=candidate.name,
                    role=normalized_role or "flex",
                    stage=stage,
                    focus=self._classify_ban_focus(
                        reasons,
                        role=normalized_role,
                        current_pick=current_pick,
                        stage=stage_key,
                    ),
                    context=self._classify_ban_context(
                        role=normalized_role,
                        revealed_enemies=revealed_enemies or [],
                    ),
                    window=self._classify_ban_window(
                        role=normalized_role,
                        draft_window=draft_window or {},
                        current_pick=current_pick,
                    ),
                    score=score,
                    reasons=tuple(reasons[:3]),
                )
            )

        recommendations.sort(key=lambda item: item.score, reverse=True)
        return recommendations[: max(1, limit)]

    def ensure_static_data(self) -> None:
        with self._lock:
            if self._champions_by_id and self._items_by_id:
                return

            cached_patch = self._load_cached_static()
            latest_patch = self._fetch_latest_patch()

            if latest_patch and latest_patch != cached_patch:
                self._refresh_static_data(latest_patch)
            elif not cached_patch and latest_patch:
                self._refresh_static_data(latest_patch)

            if not self._champions_by_id or not self._items_by_id:
                self._load_cached_static()

    def _resolve_champion(self, identifier: Any) -> Optional[dict[str, Any]]:
        if identifier is None:
            return None
        if isinstance(identifier, ChampionKnowledge):
            return self._champions_by_id.get(identifier.id)
        try:
            champion_id = int(identifier)
        except (TypeError, ValueError):
            champion_id = None
        if champion_id is not None:
            return self._champions_by_id.get(champion_id)
        return self._champions_by_name.get(_normalize_name(identifier))

    def _resolve_item(self, identifier: Any) -> Optional[dict[str, Any]]:
        if identifier is None:
            return None
        if isinstance(identifier, ItemKnowledge):
            return self._items_by_id.get(identifier.id)
        try:
            item_id = int(identifier)
        except (TypeError, ValueError):
            item_id = None
        if item_id is not None:
            return self._items_by_id.get(item_id)
        return self._items_by_name.get(_normalize_name(identifier))

    def _load_cached_static(self) -> Optional[str]:
        champions_payload = _read_json(self.cache_dir / self.locale / "champions.json")
        items_payload = _read_json(self.cache_dir / self.locale / "items.json")
        manifest = _read_json(self.cache_dir / self.locale / "manifest.json")
        if not champions_payload or not items_payload or not manifest:
            return None

        self._patch = manifest.get("patch")
        self._champions_by_id = {}
        self._champions_by_name = {}
        for raw in champions_payload.get("champions", []):
            self._champions_by_id[int(raw["id"])] = raw
            self._champions_by_name[_normalize_name(raw["name"])] = raw
            self._champions_by_name[_normalize_name(raw["key"])] = raw
        self._items_by_id = {}
        self._items_by_name = {}
        for raw in items_payload.get("items", []):
            self._items_by_id[int(raw["id"])] = raw
            self._items_by_name[_normalize_name(raw["name"])] = raw
        return self._patch

    def _load_overrides(self) -> dict[str, Any]:
        local_payload = _read_json(_OVERRIDES_PATH) or {"champions": {}}
        remote_payload = self._load_remote_overrides()
        return _deep_merge(local_payload, remote_payload)

    def refresh_remote_overrides(self) -> bool:
        if not self.remote_feed_url:
            return False
        remote_payload = self._fetch_remote_overrides(force=True)
        if not remote_payload:
            return False
        local_payload = _read_json(_OVERRIDES_PATH) or {"champions": {}}
        self._overrides = _deep_merge(local_payload, remote_payload)
        return True

    def _load_remote_overrides(self) -> dict[str, Any]:
        if not self.remote_feed_url:
            return {}
        return self._fetch_remote_overrides(force=False)

    def _fetch_remote_overrides(self, *, force: bool) -> dict[str, Any]:
        cache_path = self.cache_dir / self.locale / "remote_overrides.json"
        cached_wrapper = _read_json(cache_path) or {}
        now = time.time()
        cached_payload = cached_wrapper.get("payload") if isinstance(cached_wrapper, dict) else None
        fetched_at = float(cached_wrapper.get("fetched_at", 0) or 0) if isinstance(cached_wrapper, dict) else 0
        cached_source = str(cached_wrapper.get("source", "") or "") if isinstance(cached_wrapper, dict) else ""

        if (
            not force
            and cached_payload
            and cached_source == self.remote_feed_url
            and self.remote_feed_ttl_seconds > 0
            and (now - fetched_at) < self.remote_feed_ttl_seconds
        ):
            return cached_payload

        payload = self._read_remote_feed_source(self.remote_feed_url)
        if isinstance(payload, dict):
            wrapper = {
                "fetched_at": now,
                "source": self.remote_feed_url,
                "payload": payload,
            }
            _write_json(cache_path, wrapper)
            return payload

        if isinstance(cached_payload, dict) and cached_source == self.remote_feed_url:
            return cached_payload
        return {}

    def _read_remote_feed_source(self, source: str) -> Optional[dict[str, Any]]:
        if not source:
            return None

        if source.startswith("http://") or source.startswith("https://"):
            try:
                response = requests.get(source, timeout=_REQUEST_TIMEOUT)
                response.raise_for_status()
                payload = response.json()
                return payload if isinstance(payload, dict) else None
            except Exception:
                return None

        path = Path(source).expanduser()
        return _read_json(path)

    def _fetch_latest_patch(self) -> Optional[str]:
        try:
            response = requests.get(f"{_DD_BASE_URL}/api/versions.json", timeout=_REQUEST_TIMEOUT)
            response.raise_for_status()
            versions = response.json()
            return versions[0] if versions else None
        except Exception:
            return None

    def _refresh_static_data(self, patch: str) -> None:
        try:
            champions_response = requests.get(
                f"{_DD_BASE_URL}/cdn/{patch}/data/{self.locale}/champion.json",
                timeout=_REQUEST_TIMEOUT,
            )
            champions_response.raise_for_status()
            items_response = requests.get(
                f"{_DD_BASE_URL}/cdn/{patch}/data/{self.locale}/item.json",
                timeout=_REQUEST_TIMEOUT,
            )
            items_response.raise_for_status()
        except Exception:
            return

        champions = []
        for raw in champions_response.json().get("data", {}).values():
            champions.append(
                {
                    "id": int(raw["key"]),
                    "key": raw["id"],
                    "name": raw["name"],
                    "title": raw.get("title", ""),
                    "blurb": raw.get("blurb", ""),
                    "tags": raw.get("tags", []),
                    "partype": raw.get("partype", ""),
                    "info": raw.get("info", {}),
                    "stats": raw.get("stats", {}),
                }
            )

        items = []
        for item_id, raw in items_response.json().get("data", {}).items():
            if not raw.get("maps", {}).get("11", False):
                continue
            if raw.get("gold", {}).get("purchasable") is False:
                continue
            items.append(
                {
                    "id": int(item_id),
                    "name": raw["name"],
                    "plaintext": raw.get("plaintext", ""),
                    "description": raw.get("description", ""),
                    "tags": raw.get("tags", []),
                    "stats": raw.get("stats", {}),
                }
            )

        locale_dir = self.cache_dir / self.locale
        _write_json(locale_dir / "manifest.json", {"patch": patch, "locale": self.locale})
        _write_json(locale_dir / "champions.json", {"champions": champions})
        _write_json(locale_dir / "items.json", {"items": items})
        self._load_cached_static()

    def _load_champion_detail(self, champion_key: str) -> dict[str, Any]:
        with self._lock:
            if champion_key in self._details_cache:
                return self._details_cache[champion_key]

        cache_path = self.cache_dir / self.locale / "champion_details" / f"{champion_key}.json"
        cached = _read_json(cache_path)
        if cached:
            with self._lock:
                self._details_cache[champion_key] = cached
            return cached

        if not self._patch:
            return {}

        try:
            response = requests.get(
                f"{_DD_BASE_URL}/cdn/{self._patch}/data/{self.locale}/champion/{champion_key}.json",
                timeout=_REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            payload = response.json().get("data", {}).get(champion_key, {})
            if payload:
                _write_json(cache_path, payload)
            with self._lock:
                self._details_cache[champion_key] = payload
            return payload
        except Exception:
            return {}

    def _infer_archetype(self, champion: dict[str, Any]) -> str:
        name = champion["name"]
        tags = set(champion.get("tags", []))
        stats = champion.get("stats", {})
        attack_range = stats.get("attackrange", 0)

        if name in _ENCHANTERS:
            return "enchanter"
        if name in _ENGAGE_SUPPORTS:
            return "engage_support"
        if name in _POKE_SUPPORTS:
            return "poke_support"
        if name in _CONTROL_MAGES:
            return "control_mage"
        if name in _JUGGERNAUTS:
            return "juggernaut"
        if name in _SKIRMISHERS:
            return "skirmisher"
        if "Marksman" in tags:
            return "marksman"
        if "Assassin" in tags:
            return "assassin"
        if "Support" in tags and "Tank" in tags:
            return "engage_support"
        if "Support" in tags:
            return "enchanter" if attack_range >= 500 else "engage_support"
        if "Mage" in tags:
            return "control_mage" if attack_range >= 525 else "burst_mage"
        if "Tank" in tags and "Fighter" in tags:
            return "juggernaut"
        if "Tank" in tags:
            return "tank"
        if "Fighter" in tags:
            return "bruiser" if attack_range <= 250 else "skirmisher"
        return "generalist"

    def _power_spikes_for(self, champion: dict[str, Any] | ChampionKnowledge) -> tuple[str, ...]:
        champion_name = champion.name if isinstance(champion, ChampionKnowledge) else (champion.get("name") or champion.get("key"))
        override = self._champion_override(champion_name)
        if override and override.get("power_spikes"):
            return tuple(override["power_spikes"])
        if isinstance(champion, ChampionKnowledge):
            archetype = champion.archetype
        else:
            archetype = self._infer_archetype(champion)
        return _ARCHETYPE_POWER_SPIKES.get(
            archetype,
            (
                "nivel 6",
                "primeiro item completo",
                "dois itens quando a luta comecar a girar no teu kit",
            ),
        )

    def _coach_tags_for_item(self, item: dict[str, Any]) -> tuple[str, ...]:
        text = f"{item.get('plaintext', '')} {item.get('description', '')}".lower()
        stats = item.get("stats", {})
        tags = set()

        if stats.get("FlatArmorMod", 0) > 0:
            tags.add("armor")
        if stats.get("FlatSpellBlockMod", 0) > 0:
            tags.add("magic_resist")
        if "feridas dolorosas" in text or "ferimento" in text:
            tags.add("anti_heal")
        if "armorpenetration" in {tag.lower() for tag in item.get("tags", [])} or "penetração de armadura" in text:
            tags.add("armor_pen")
        if "penetração mágica" in text or "resistência mágica" in text and "supera" in text:
            tags.add("magic_pen")
        if "tenacidade" in text:
            tags.add("tenacity")
        return tuple(sorted(tags))

    def _threat_counts(self, enemy_profiles: list[ChampionKnowledge]) -> dict[str, int]:
        counts = {
            "engage": 0,
            "assassin": 0,
            "tank": 0,
            "poke": 0,
            "sustain": 0,
            "hard_cc": 0,
        }
        for champion in enemy_profiles:
            if champion.archetype in {"engage_support", "tank", "juggernaut"}:
                counts["engage"] += 1
            if champion.archetype == "assassin":
                counts["assassin"] += 1
            if champion.archetype in {"tank", "juggernaut"}:
                counts["tank"] += 1
            if champion.archetype in {"control_mage", "poke_support", "marksman"}:
                counts["poke"] += 1
            if champion.name in _SUSTAIN_CHAMPS:
                counts["sustain"] += 1
            if champion.name in _HARD_CC_CHAMPS or champion.archetype == "engage_support":
                counts["hard_cc"] += 1
        return counts

    def _infer_comp_style(self, threats: dict[str, int]) -> str:
        if threats["tank"] >= 2 and threats["poke"] >= 1:
            return "front-to-back pesada"
        if threats["assassin"] >= 2:
            return "pick e explosao"
        if threats["poke"] >= 3:
            return "poke e desgaste"
        if threats["engage"] >= 2:
            return "engage reto"
        return "comp equilibrada"

    def _pressure_points(self, threats: dict[str, int]) -> list[str]:
        points = []
        if threats["hard_cc"] >= 2:
            points.append("respeitar cadeia de controle e nao entrar sem resposta")
        if threats["assassin"] >= 1:
            points.append("jogar fight com linha de visao e cobertura")
        if threats["tank"] >= 2:
            points.append("preparar luta longa e atravessar front line com paciencia")
        if threats["sustain"] >= 1:
            points.append("cortar cura no timing certo")
        if not points:
            points.append("executar lane, reset e objetivo no tempo certo")
        return points

    def _item_picks(self, champion: ChampionKnowledge, need: str, limit: int = 1) -> list[str]:
        """Return up to *limit* item names for *champion* and *need* type."""
        champ_overrides = _CHAMPION_ITEM_OVERRIDES.get(champion.name, {})
        items = champ_overrides.get(need)
        if items is None:
            archetype_map = _ARCHETYPE_ITEM_MAP.get(champion.archetype, {})
            items = archetype_map.get(need, [])
        return items[:limit]

    def recommend_items_for_champion(
        self,
        champion_name: Any,
        need_types: list[str] | None = None,
    ) -> dict[str, list[str]]:
        """Public API: return named items for each need type.

        *need_types* defaults to all available types if ``None``.
        """
        champion = self.get_champion(champion_name)
        if not champion:
            return {}
        all_needs = need_types or [
            "anti_heal", "armor_pen", "magic_pen", "defensive",
            "tenacity", "anti_burst", "vs_tanks",
        ]
        return {need: self._item_picks(champion, need, limit=2) for need in all_needs}

    def _build_focus(self, champion: ChampionKnowledge, threats: dict[str, int]) -> list[str]:
        focus = []
        if threats["hard_cc"] >= 2:
            tenacity = self._item_picks(champion, "tenacity", 1)
            if tenacity:
                focus.append(f"{tenacity[0]} contra controle pesado")
            else:
                focus.append("tenacidade contra controle pesado")
        if threats["assassin"] >= 2:
            defenses = self._item_picks(champion, "anti_burst", 2)
            if defenses:
                focus.append(f"{' ou '.join(defenses)} como seguro contra burst")
            else:
                focus.append("seguro defensivo antes de build full ganancia")
        if threats["tank"] >= 2:
            pen_items = self._item_picks(champion, "vs_tanks", 2)
            if pen_items:
                focus.append(f"{' e '.join(pen_items)} pra atravessar a front line")
            else:
                focus.append("penetracao e dano consistente para luta longa")
        if threats["sustain"] >= 1:
            heal_items = self._item_picks(champion, "anti_heal", 1)
            if heal_items:
                focus.append(f"{heal_items[0]} contra o sustain deles")
            else:
                focus.append("anti-heal no radar antes da fight desandar")
        if not focus:
            focus.append(f"fecha o pico base de {champion.name} e adapta depois do primeiro recall forte")
        return focus

    def _default_lane_plan(self, champion: ChampionKnowledge, role: str) -> str:
        archetype = champion.archetype
        if archetype == "marksman":
            return f"com {champion.name}, joga por wave limpa, espacamento e entrada segura na luta; teu dano cresce mais que tua capacidade de perdoar erro"
        if archetype == "assassin":
            return f"com {champion.name}, controla wave so o suficiente para abrir mapa e cobra janela curta; teu boneco odeia fight frontal longa"
        if archetype in {"control_mage", "burst_mage"}:
            return f"com {champion.name}, usa alcance e wave para mandar no ritmo da lane e transformar prioridade em pressao de mapa"
        if archetype in {"juggernaut", "bruiser", "skirmisher"}:
            return f"com {champion.name}, a lane vive de espaco e troca bem escolhida; nao entrega wave ruim nem luta sem recurso"
        if archetype in {"engage_support", "enchanter", "poke_support"}:
            return f"de {champion.name} no suporte, teu valor vem de controlar a primeira janela do bot e preparar o rio antes do objetivo"
        if archetype == "tank":
            return f"com {champion.name}, segura o early sem desespero e prepara a partida para a teamfight onde teu corpo manda no mapa"
        return f"com {champion.name}, joga o basico forte, respeita teu primeiro pico e faz a lane servir ao plano da partida"

    def _default_opening_plan(self, champion: ChampionKnowledge, role: str) -> str:
        archetype = champion.archetype
        if role == "jungle":
            return f"de {champion.name} na jungle, teu early e ler prioridade de lane e escolher gank ou full clear sem flipar o mapa"
        if role == "support":
            return f"de {champion.name} no suporte, os primeiros minutos sao de brush, nivel 2 e controle do rio"
        if role == "bottom":
            return f"de {champion.name} no bot, os primeiros waves definem tua liberdade; nao entrega o nivel 2 nem a wave 3 de graca"
        if role == "mid":
            return f"de {champion.name} no mid, teu comeco e wave, recurso e visao lateral para nao virar alvo de gank burro"
        if role == "top":
            return f"de {champion.name} no top, os primeiros minutos sao sobre wave e espaco; nao luta sem motivo com a lane no lugar errado"
        if archetype == "assassin":
            return f"de {champion.name}, teu early e sobreviver onde precisa e preparar a primeira janela em que teu kit ameaca kill real"
        if archetype == "marksman":
            return f"de {champion.name}, teu opening e garantir wave jogavel e vida suficiente pra nao sair da lane na marra"
        return f"de {champion.name}, comeca pela wave, pela visao e pelo primeiro reset certo"

    def _default_first_reset_focus(self, champion: ChampionKnowledge, role: str) -> str:
        archetype = champion.archetype
        if archetype == "marksman":
            return "volta com componente de dano e vida suficiente para nao perder a lane na volta"
        if archetype == "assassin":
            return "compra letalidade ou burst cedo e garante controle lateral de visao"
        if archetype in {"control_mage", "burst_mage"}:
            return "prioriza mana, wave clear ou burst para liberar teu mapa"
        if archetype in {"juggernaut", "bruiser", "skirmisher"}:
            return "compra ferramenta de troca e segura a wave num ponto em que tu possas escolher a luta"
        if archetype in {"engage_support", "enchanter", "poke_support"}:
            return "volta com recurso para disputa de rio, pink e o primeiro all-in ou peel decente"
        if archetype == "tank":
            return "fecha defesa basica e acelera teu primeiro item funcional"
        return "faz o primeiro reset te deixar mais forte no mapa, nao so menos fraco"

    def _default_lane_windows(self, champion: ChampionKnowledge, role: str) -> list[str]:
        archetype = champion.archetype
        if role == "support":
            return [
                "niveis 1-2: disputa brush e a corrida pelo nivel 2",
                "nivel 3: procura engage limpa ou peel bom com wave curta",
                "nivel 6: tua ult precisa virar summoner, kill ou objetivo",
            ]
        if role == "jungle":
            return [
                "primeiro clear: escolhe rota em cima da prioridade das lanes",
                "nivel 3-4: ganka so lane com setup ou wave jogavel",
                "nivel 6: acelera o lado forte do mapa e prepara objetivo",
            ]
        if role == "bottom":
            return [
                "niveis 1-3: garante wave jogavel e respeita a corrida pelo nivel 2",
                "primeiro recall: volta com dano suficiente para nao perder a lane",
                "nivel 6: luta so com spacing e cobertura, nao no desespero",
            ]
        if role == "mid":
            return [
                "niveis 1-3: joga pela wave e nao entrega janela de all-in",
                "nivel 6: decide se tu tens kill, push ou roam de verdade",
                "primeiro item: transforma prioridade em mapa, nao so em farm",
            ]
        if role == "top":
            return [
                "niveis 1-3: decide a wave antes de decidir a luta",
                "nivel 6: respeita all-in e recurso de sustain ou ult",
                "primeiro item: usa teu spike pra travar side ou chamar jungle",
            ]
        if archetype == "assassin":
            return [
                "niveis 1-3: sobrevive sem perder a wave de graca",
                "nivel 6: tua primeira janela real de burst precisa ser limpa",
                "primeiro item: acelera pickoff, nao luta frontal longa",
            ]
        if archetype == "marksman":
            return [
                "niveis 1-3: protege HP e wave ao mesmo tempo",
                "primeiro recall: volta com componente forte de DPS",
                "dois itens: teu dano ja precisa decidir objetivo",
            ]
        return [
            "early: joga pela wave e pela distancia certa",
            "nivel 6: identifica tua primeira janela real de pressao",
            "primeiro item: converte spike em mapa, nao em flip",
        ]

    def _matchup_lane_windows(self, mine: ChampionKnowledge, enemy: ChampionKnowledge, role: str | None) -> list[str]:
        role_key = self._normalize_role(role or "")
        enemy_arch = enemy.archetype
        if role_key == "mid" and enemy_arch == "assassin":
            return [
                "niveis 1-3: segura a wave num ponto curto e nao entrega all-in cedo",
                "nivel 6: tracka flash e ult antes de andar sem visao lateral",
                "primeiro item: joga por push e resposta no mapa, nao por ego em troca longa",
            ]
        if role_key == "top" and enemy_arch in {"juggernaut", "bruiser"}:
            return [
                "niveis 1-3: decide a wave antes da troca porque o all-in deles pune cedo",
                "nivel 6: respeita janela de ult e sustain, principalmente com wave longa",
                "primeiro item: usa teu spike para chamar jungle ou travar side, nao para flipar dive",
            ]
        if role_key == "bottom" and enemy_arch in {"engage_support", "marksman"}:
            return [
                "niveis 1-2: a corrida pelo nivel 2 define se tu pode jogar a lane",
                "primeiro recall: volta com dano e vida para nao perder push e placa",
                "nivel 6: fighta so com spacing e cover do suporte, sem andar reto no engage",
            ]
        if role_key == "support":
            return [
                "niveis 1-2: brush e nivel 2 valem mais que poke solto",
                "primeiro recall: pink e recurso para o rio importam mais que inventar roam burro",
                "nivel 6: tua ult precisa virar objetivo, kill ou reset ruim pros caras",
            ]
        return self._default_lane_windows(mine, role_key)

    def _recommended_setup(self, mine: ChampionKnowledge, enemy: ChampionKnowledge, role: str | None) -> str:
        role_key = self._normalize_role(role or "")
        enemy_arch = enemy.archetype
        if role_key in {"mid", "top"} and enemy_arch == "assassin":
            return "prioriza setup defensivo e respeita cleanse/barreira/exaustao se teu campeao aceitar essa troca"
        if role_key == "bottom" and enemy_arch in {"engage_support", "tank"}:
            return "entra com feitiço de sobrevivencia e posicionamento para nao morrer na primeira engage limpa"
        if role_key == "support" and enemy_arch in {"marksman", "enchanter", "poke_support"}:
            return "escolhe setup que te deixe ganhar nivel 2 e controlar o rio cedo, nao so escalar passivo"
        if mine.archetype in {"control_mage", "burst_mage"} and enemy_arch in {"tank", "juggernaut"}:
            return "setup de lane e mana vale mais que greed puro; teu kit precisa chegar inteiro no primeiro objetivo"
        if mine.archetype == "marksman":
            return "setup de dano consistente e seguranca vale mais que greed de all-in cedo"
        if mine.archetype == "assassin":
            return "setup que preserve tua janela de burst no nivel 6 costuma valer mais que greed de lane"
        return "entra com setup que fortaleça tua primeira janela forte e nao te deixe sem resposta no all-in inimigo"

    def _lane_win_condition(self, mine: ChampionKnowledge, enemy: ChampionKnowledge, role: str | None) -> str:
        role_key = self._normalize_role(role or "")
        enemy_arch = enemy.archetype
        if role_key == "mid":
            if enemy_arch == "assassin":
                return "manter wave jogavel, nao dar all-in limpo no 6 e usar push para chegar primeiro no mapa"
            if enemy_arch == "control_mage":
                return "ganhar espaço na wave e transformar push em reset, roam ou objetivo antes do mid travar"
            if enemy_arch == "burst_mage":
                return "forçar a troca no timing em que o burst dele está incompleto e não deixar a lane virar skillcheck seco"
            return "manter controle da wave e entrar primeiro no ciclo de reset e mapa"
        if role_key == "top":
            if enemy_arch in {"juggernaut", "bruiser"}:
                return "quebrar o ritmo da troca longa e chegar no primeiro item com a lane ainda tua"
            if enemy_arch == "tank":
                return "punir a lane antes do primeiro item fechar e impedir que o top vire só front-to-back confortável"
            if enemy_arch == "skirmisher":
                return "ditar o espaçamento da side e não deixar o duelo ficar limpo demais para o rival"
            return "travar a wave no teu tempo e converter o primeiro item em pressão real de side ou mapa"
        if role_key == "bottom":
            if enemy.name in _ENGAGE_SUPPORTS or enemy_arch in {"engage_support", "tank"}:
                return "preservar HP, segurar spacing e passar pelo nivel 2 sem dar engage limpa"
            if enemy.name in _ENCHANTERS or enemy_arch == "enchanter":
                return "manter a wave jogavel e impedir que a lane deles escale limpa com sustain e buff"
            if enemy_arch == "marksman":
                return "disputar push e spacing sem perder HP demais antes do primeiro item"
            return "preservar HP e spacing ate o primeiro item sem perder totalmente a pressao da wave"
        if role_key == "support":
            if enemy.name in _ENGAGE_SUPPORTS or enemy_arch == "engage_support":
                return "ganhar ou neutralizar o nivel 2 e controlar brush antes da primeira engage séria"
            if enemy.name in _ENCHANTERS or enemy_arch == "enchanter":
                return "tirar conforto do carry inimigo cedo e não deixar a lane deles jogar em sustain grátis"
            if enemy.name in _POKE_SUPPORTS or enemy_arch == "poke_support":
                return "preservar vida, disputar brush e fazer a troca curta sair antes do poke te cozinhar"
            return "ganhar ou segurar o nivel 2, controlar brush e fazer o rio nascer melhor para teu duo"
        if mine.archetype == "marksman":
            return "sair da lane inteiro o bastante para teu primeiro item realmente existir"
        if mine.archetype == "assassin":
            return "preservar a lane ate tua janela de burst e atacar quando o rival gastar o recurso chave"
        if mine.archetype in {"control_mage", "burst_mage"}:
            return "mandar na wave e no espaço para entrar primeiro em reset, objetivo e roam"
        if mine.archetype in {"skirmisher", "bruiser", "juggernaut"}:
            return "fazer a lane girar no teu tempo e transformar o primeiro item em pressão real"
        return "chegar no teu primeiro pico sem entregar a lane nas janelas fortes do inimigo"

    def _lane_fail_condition(self, mine: ChampionKnowledge, enemy: ChampionKnowledge, role: str | None) -> str:
        role_key = self._normalize_role(role or "")
        enemy_arch = enemy.archetype
        if role_key == "mid":
            if enemy_arch == "assassin":
                return "andar sem recurso defensivo ou sem visão lateral quando o all-in já existe"
            if enemy_arch == "control_mage":
                return "perder a wave e o espaço no mesmo ciclo, deixando o rival ditar reset e mapa"
            if enemy_arch == "burst_mage":
                return "entrar na troca com cooldown torto e transformar a lane num duelo seco que favorece o burst deles"
            return "ceder wave e prioridade cedo demais e jogar o mid no tempo do rival"
        if role_key == "top":
            if enemy_arch in {"juggernaut", "bruiser"}:
                return "comprar luta longa na wave errada e deixar o topo virar side impossível cedo"
            if enemy_arch == "tank":
                return "deixar o tanque fechar item e entrar inteiro na primeira luta sem pagar nada na lane"
            if enemy_arch == "skirmisher":
                return "dar duelo limpo demais e deixar a side lane virar território do rival"
            return "perder a wave e a troca no mesmo tempo, entregando o topo e o primeiro mapa"
        if role_key == "bottom":
            if enemy.name in _ENGAGE_SUPPORTS or enemy_arch in {"engage_support", "tank"}:
                return "perder o nivel 2 ou andar sem cover quando a engage deles já está pronta"
            if enemy.name in _ENCHANTERS or enemy_arch == "enchanter":
                return "deixar a lane deles escalar sem pressão e chegar no primeiro item sempre atrás"
            if enemy_arch == "marksman":
                return "trocar HP por ego cedo e perder wave, reset e pressão no mesmo ciclo"
            return "perder o nivel 2, tomar engage limpa e chegar no primeiro recall sem vida nem wave"
        if role_key == "support":
            if enemy.name in _ENGAGE_SUPPORTS or enemy_arch == "engage_support":
                return "ceder brush e gastar peel ou engage antes da primeira entrada forte"
            if enemy.name in _ENCHANTERS or enemy_arch == "enchanter":
                return "deixar o carry inimigo jogar confortável demais e perder a lane no ritmo deles"
            if enemy.name in _POKE_SUPPORTS or enemy_arch == "poke_support":
                return "tomar poke sem resposta até tua lane perder espaço, vida e controle de rio"
            return "ceder brush e gastar a resposta principal antes da primeira engage séria"
        if mine.archetype == "marksman":
            return "trocar HP por ego cedo e transformar teu primeiro item em reset atrasado"
        if mine.archetype == "assassin":
            return "forçar lane reta demais antes de ter janela real de burst"
        if mine.archetype in {"control_mage", "burst_mage"}:
            return "perder a wave e o espaço no mesmo ciclo, ficando presa no meio sem controle"
        if mine.archetype in {"skirmisher", "bruiser", "juggernaut"}:
            return "entrar na luta no timing do rival e alongar troca quando tua janela já passou"
        return "errar a primeira janela forte e deixar a lane ser jogada no tempo do inimigo"

    def _pick_lane_plan_summary(
        self,
        mine: ChampionKnowledge,
        enemy_profiles: list[ChampionKnowledge],
        *,
        role: str | None = None,
        enemy_anchor: Any | None = None,
    ) -> str:
        role_key = self._normalize_role(role or "")
        enemy = self.get_champion(enemy_anchor) if enemy_anchor else None
        threats = self._threat_counts(enemy_profiles)
        enemy_arches = {champ.archetype for champ in enemy_profiles}
        has_marksman = "marksman" in enemy_arches
        has_engage = any(
            champ.name in _ENGAGE_SUPPORTS or champ.archetype in {"engage_support", "tank"}
            for champ in enemy_profiles
        )
        has_enchanter = any(
            champ.name in _ENCHANTERS or champ.archetype == "enchanter"
            for champ in enemy_profiles
        )
        has_poke = any(
            champ.name in _POKE_SUPPORTS or champ.archetype == "poke_support"
            for champ in enemy_profiles
        )

        if role_key in {"bottom", "support"} and enemy_profiles:
            if has_engage and has_marksman:
                return "quebrar engage, respeitar push cedo e sair inteiro para teu primeiro item"
            if has_enchanter and has_marksman:
                return "pressionar a lane cedo e impedir escala limpa do duo inimigo"
            if has_poke and has_marksman:
                return "ganhar espaco na wave, disputar brush e nao deixar poke cozinhar teu reset"
            if has_engage:
                return "quebrar engage e estabilizar a lane ate teu primeiro pico"
            if has_enchanter:
                return "manter pressao jogavel e impedir escala limpa da lane"
            if has_poke:
                return "ganhar espaco na wave sem deixar o poke ditar teu reset"
            if has_marksman:
                return "jogar por wave e spacing ate teu primeiro item entrar"

        if role_key == "mid" and enemy:
            if enemy.archetype == "assassin":
                if threats.get("hard_cc", 0) >= 2 or threats.get("engage", 0) >= 2:
                    return "sobreviver ao all-in, manter wave jogavel e resetar sem abrir engage facil"
                return "sobreviver ao all-in e transformar push em mapa"
            if enemy.archetype == "control_mage":
                if threats.get("assassin", 0) >= 2:
                    return "ganhar push sem se expor e usar reset para nao abrir pickoff lateral"
                return "ganhar push e reset para chegar primeiro no mapa"
            if enemy.archetype == "burst_mage":
                if threats.get("poke", 0) >= 2:
                    return "trocar em janela curta e sair da lane com reset limpo antes do poke empilhar"
                return "trocar em janela curta e negar burst limpo"

        if role_key == "top" and enemy:
            if enemy.archetype in {"juggernaut", "bruiser"}:
                if threats.get("assassin", 0) >= 2 or threats.get("engage", 0) >= 2:
                    return "segurar spacing na side e guardar recurso para nao virar engage gratis no mapa"
                return "jogar por spacing curto e nao deixar troca longa te prender"
            if enemy.archetype == "tank":
                if threats.get("tank", 0) >= 2:
                    return "punir cedo e impedir que a side vire front line dupla sem custo"
                return "punir cedo e nao deixar a lane virar front line gratis"
            if enemy.archetype == "skirmisher":
                if threats.get("hard_cc", 0) >= 2:
                    return "dominar side lane sem dar janela de pickoff quando sair da wave"
                return "dominar side lane sem dar duelo limpo demais"

        if role_key == "jungle":
            if threats.get("hard_cc", 0) >= 2:
                return "acelerar o primeiro ciclo sem flipar entrada em muito controle"
            return "ditar a primeira janela de gank e objetivo"
        if threats.get("assassin", 0) >= 2:
            return "sobreviver ao burst inicial e escalar a lane com seguranca"
        if threats.get("tank", 0) >= 2:
            return "passar da lane limpo e entrar em luta longa no teu timing"
        return "jogar no teu pico de poder e transformar lane em mapa"

    def _default_first_item_plan(self, champion: ChampionKnowledge, role: str, build_focus: list[str]) -> str:
        if build_focus:
            return f"teu primeiro item precisa conversar com {build_focus[0]}"
        archetype = champion.archetype
        if role == "support":
            return "fecha o primeiro utilitario que te deixe disputar rio e proteger ou puxar engage"
        if role == "jungle":
            return "o primeiro item tem que acelerar teu ritmo de gank ou tua entrada no objetivo"
        if archetype == "marksman":
            return "prioriza dano consistente para a lane nao te expulsar no segundo ciclo"
        if archetype == "assassin":
            return "teu primeiro item precisa abrir pickoff e ameaçar all-in limpo"
        if archetype in {"control_mage", "burst_mage"}:
            return "teu primeiro item precisa liberar wave e controle de espaço"
        if archetype in {"tank", "engage_support"}:
            return "teu primeiro item precisa te dar corpo para entrar e continuar vivo"
        return "o primeiro item precisa reforçar teu plano da lane, nao so tapar buraco"

    def _draft_reset_adjustment(self, champion: ChampionKnowledge, threats: dict[str, int], role: str) -> str:
        if role in {"bottom", "support"}:
            if threats["engage"] >= 2:
                return "reseta com wave protegida, porque voltar seco contra engage reta e pedir all-in"
            if threats["poke"] >= 2:
                return "nao segura reset atrasado sem vida, porque poke empilha e te expulsa do tempo da lane"
        if role == "mid":
            if threats["assassin"] >= 2 or threats["hard_cc"] >= 2:
                return "reseta com visao lateral e wave limpa para nao abrir pickoff no caminho"
            if threats["poke"] >= 2:
                return "usa reset cedo quando ganhar push, antes da lane virar desgaste puro"
        if role == "top":
            if threats["tank"] >= 2:
                return "nao atrasa reset, porque front line dupla cresce demais se o topo respirar gratis"
            if threats["assassin"] >= 1 or threats["engage"] >= 2:
                return "reseta sem quebrar teu tempo de side, senao o mapa te cobra longe da wave"
        if role == "jungle":
            return "teu reset precisa cair antes da primeira briga grande de rio ou objetivo"
        return "reseta no ciclo em que tua wave e teu mapa ainda te deixam voltar forte"

    def _draft_map_plan_summary(
        self,
        champion: ChampionKnowledge,
        threats: dict[str, int],
        role: str,
        *,
        ally_identity: str = "tempo",
    ) -> str:
        archetype = champion.archetype
        if ally_identity == "pick":
            return "joga o mapa por visao lateral, pickoff e numero antes do objetivo"
        if ally_identity == "dive":
            return "teu mapa quer angulo de engage e follow-up, nao setup lento demais"
        if ally_identity == "front-to-back":
            return "teu mapa quer reset organizado e objetivo montado antes da luta"
        if ally_identity == "side":
            return "teu mapa quer side lane puxando resposta antes da fight grande"
        if role == "mid":
            if threats["assassin"] >= 2:
                return "joga por push curto e cobertura, nao por lateral longa sem informacao"
            return "usa a lane para empurrar reset e chegar primeiro em rio, invade ou lado forte"
        if role == "top":
            if archetype in {"skirmisher", "bruiser"}:
                return "teu mapa quer side lane viva e entrada boa depois que a pressao puxar resposta"
            if threats["tank"] >= 2:
                return "cobra side cedo, antes que o jogo deles vire front-to-back confortavel"
            return "segura a side sem entregar tempo gratis e entra na luta quando teu pico abrir"
        if role in {"bottom", "support"}:
            if threats["engage"] >= 2:
                return "joga o mapa por wave segura, rio preparado e objetivo sem facecheck torto"
            return "usa push e reset para chegar primeiro em rio e objetivo"
        if role == "jungle":
            return "teu mapa quer primeira janela de gank bem lida e objetivo jogado com prioridade"
        if archetype in {"control_mage", "burst_mage"}:
            return "transforma push em presenca de mapa, nao em lane parada"
        if archetype in {"skirmisher", "bruiser"}:
            return "puxa side quando o mapa abrir e entra na luta pelo angulo certo"
        return "joga o mapa no tempo do teu reset e do teu primeiro spike"

    def _draft_fight_plan_summary(
        self,
        champion: ChampionKnowledge,
        threats: dict[str, int],
        role: str,
        *,
        ally_identity: str = "tempo",
    ) -> str:
        archetype = champion.archetype
        if ally_identity == "pick":
            return "tua comp quer achar alvo fora de posicao antes da luta abrir inteira"
        if ally_identity == "dive":
            return "tua comp quer entrar em dois tempos e colapsar rapido no mesmo alvo"
        if ally_identity == "front-to-back":
            return "tua comp quer lutar em bloco, com linha montada e alvo batido de frente"
        if ally_identity == "side":
            return "tua comp luta melhor depois que a side puxar resposta e abrir angulo"
        if threats["tank"] >= 2:
            return "tua comp precisa aceitar luta longa e atravessar front line com paciencia"
        if threats["assassin"] >= 2:
            return "tua fight pede cobertura e entrada limpa, nao luta quebrada em dois blocos"
        if threats["poke"] >= 3:
            return "tua comp quer encurtar setup inimigo e nao ficar tomando desgaste antes do all-in"
        if role == "top" and archetype in {"skirmisher", "bruiser"}:
            return "tu entra melhor quando a side ja puxou resposta e a luta abre em dois tempos"
        if role in {"bottom", "support"} and threats["engage"] >= 2:
            return "tua fight precisa de spacing limpo e resposta pronta para a primeira engage"
        return "tua comp quer a luta no teu timing de spike, nao no impulso deles"

    def _draft_team_plan_summary(self, ally_identity: str, role: str) -> str:
        if ally_identity == "pick":
            return "quebrar visao, achar alvo e entrar em objetivo com vantagem numerica"
        if ally_identity == "dive":
            return "forcar engage encadeada e matar backline antes da fight alongar"
        if ally_identity == "front-to-back":
            return "montar objetivo cedo e lutar em bloco com front line protegendo teu dano"
        if ally_identity == "side":
            return "abrir side lane, puxar resposta e so depois chamar a luta principal"
        if role == "jungle":
            return "usar prioridade e reset para decidir o primeiro grande objetivo"
        return "jogar no timing do teu spike e converter espaco em objetivo"

    def _default_mid_game_job(self, champion: ChampionKnowledge, role: str) -> str:
        archetype = champion.archetype
        if archetype == "marksman":
            return "jogar atras da linha de frente e converter objetivo com DPS constante"
        if archetype == "assassin":
            return "procurar flank, cortar visao e matar alvo sem front line"
        if archetype in {"control_mage", "burst_mage"}:
            return "mandar no choke de objetivo e transformar range em pickoff ou zoneamento"
        if archetype in {"juggernaut", "bruiser", "skirmisher"}:
            return "pressionar side lane e entrar na fight quando o mapa abrir"
        if archetype in {"engage_support", "tank"}:
            return "preparar visao e ser o gatilho da engage ou do contra-engage"
        if archetype in {"enchanter", "poke_support"}:
            return "proteger carry e desgastar antes da luta virar all-in"
        return "jogar em volta do objetivo e do teu timing de item"

    def _default_situational_items(self, champion: ChampionKnowledge) -> list[str]:
        items = []
        anti_heal = self._item_picks(champion, "anti_heal", 1)
        defensive = self._item_picks(champion, "anti_burst", 1)
        pen = self._item_picks(champion, "vs_tanks", 1) or self._item_picks(champion, "armor_pen", 1) or self._item_picks(champion, "magic_pen", 1)
        if anti_heal:
            items.append(f"{anti_heal[0]} contra sustain")
        if pen:
            items.append(f"{pen[0]} contra front line pesada")
        if defensive:
            items.append(f"{defensive[0]} se precisar de seguro")
        if not items:
            items.append("adaptação situacional ao tab inimigo")
        return items[:3]

    def _allied_profiles(self, mine: ChampionKnowledge, allies: list[dict[str, Any]]) -> list[ChampionKnowledge]:
        profiles = [mine]
        seen = {_normalize_name(mine.name)}
        for ally in allies or []:
            ally_name = (ally or {}).get("champion")
            ally_profile = self.get_champion(ally_name)
            if not ally_profile:
                continue
            normalized_name = _normalize_name(ally_profile.name)
            if normalized_name in seen:
                continue
            seen.add(normalized_name)
            profiles.append(ally_profile)
        return profiles

    def _infer_allied_comp_identity(self, ally_profiles: list[ChampionKnowledge], threats: dict[str, int]) -> str:
        archetypes = {champ.archetype for champ in ally_profiles}
        skirmish_core = sum(1 for champ in ally_profiles if champ.archetype in {"skirmisher", "bruiser"}) >= 2
        if any(arch in archetypes for arch in {"tank", "engage_support"}) and "marksman" in archetypes:
            return "front-to-back"
        if threats["engage"] >= 1 and any(arch in archetypes for arch in {"assassin", "bruiser", "skirmisher", "burst_mage"}):
            return "dive"
        if skirmish_core and any(arch in archetypes for arch in {"assassin", "control_mage", "burst_mage"}):
            return "dive"
        if threats["hard_cc"] >= 1 and any(arch in archetypes for arch in {"assassin", "burst_mage", "control_mage"}):
            return "pick"
        if sum(1 for champ in ally_profiles if champ.archetype in {"skirmisher", "bruiser", "juggernaut"}) >= 2:
            return "side"
        return "tempo"

    def _champion_override(self, champion_name: Any) -> dict[str, Any]:
        champions = self._overrides.get("champions", {})
        return champions.get(_normalize_name(champion_name), {})

    def _role_override(self, champion_name: Any, role: str | None = None) -> dict[str, Any]:
        override = self._champion_override(champion_name)
        roles = override.get("roles", {})
        if role:
            role_key = self._normalize_role(role)
            if role_key in roles:
                return roles[role_key]
        return {}

    def _matchup_override(self, my_champion: Any, enemy_champion: Any, role: str | None = None) -> dict[str, Any]:
        role_override = self._role_override(my_champion, role)
        matchups = role_override.get("matchups", {})
        return matchups.get(_normalize_name(enemy_champion), {})

    def _duo_synergy_override(self, first_champion: Any, second_champion: Any) -> dict[str, Any]:
        synergies = self._overrides.get("synergies", {})
        duo_map = synergies.get("duo", {})
        key = self._synergy_key(first_champion, second_champion)
        return duo_map.get(key, {})

    def _jungle_lane_synergy_override(self, jungler: Any, laner: Any) -> dict[str, Any]:
        synergies = self._overrides.get("synergies", {})
        jungle_map = synergies.get("jungle_lane", {})
        key = f"{_normalize_name(jungler)}+{_normalize_name(laner)}"
        return jungle_map.get(key, {})

    def _synergy_key(self, *champions: Any) -> str:
        normalized = sorted(_normalize_name(champion) for champion in champions if champion)
        return "+".join(normalized)

    def _infer_duo_synergy(self, first: ChampionKnowledge, second: ChampionKnowledge) -> Optional[dict[str, Any]]:
        pair = {first.archetype, second.archetype}
        names = [first.name, second.name]

        if "engage_support" in pair and "marksman" in pair:
            return {
                "label": "all-in de bot lane",
                "plan": f"{names[0]} com {names[1]} quer nível 2, brush control e engage curta quando a wave ajudar.",
                "spike": "o primeiro pico é no nível 2 e volta a ficar forte no primeiro reset com recurso de lane.",
                "champions": names,
            }
        if "enchanter" in pair and "marksman" in pair:
            return {
                "label": "escala com pressão limpa",
                "plan": f"{names[0]} com {names[1]} quer push disciplinado, troca curta e transição para objetivo com carry protegido.",
                "spike": "a dupla cresce muito quando o primeiro item do carry e o utilitário do suporte entram juntos.",
                "champions": names,
            }
        if "poke_support" in pair and "marksman" in pair:
            return {
                "label": "poke e torre cedo",
                "plan": f"{names[0]} com {names[1]} quer wave empurrada, HP advantage e placa antes do mapa abrir.",
                "spike": "o pico vem no primeiro recall limpo, quando poke e push passam a custar torre ou reset ruim.",
                "champions": names,
            }
        return None

    def _infer_jungle_lane_synergy(self, jungle: ChampionKnowledge, lane: ChampionKnowledge) -> Optional[dict[str, Any]]:
        if jungle.archetype in {"tank", "engage_support", "bruiser"} and lane.archetype in {"control_mage", "burst_mage", "assassin"}:
            return {
                "label": "setup de pickoff e gank",
                "plan": f"{jungle.name} com {lane.name} quer wave preparada e entrada sincronizada para matar ou forçar flash.",
                "spike": "o duo cresce cedo, assim que a lane libera prioridade e o jungler fecha rota de entrada.",
                "champions": [jungle.name, lane.name],
            }
        if jungle.archetype in {"skirmisher", "bruiser"} and lane.archetype in {"juggernaut", "skirmisher"}:
            return {
                "label": "2v2 forte de rio",
                "plan": f"{jungle.name} com {lane.name} quer disputa de escaramuça cedo e pressão de lado forte antes do objetivo.",
                "spike": "a dupla acende no nível 3 a 6, quando ambos conseguem transformar prioridade em luta real.",
                "champions": [jungle.name, lane.name],
            }
        if jungle.archetype in {"tank", "bruiser"} and lane.archetype == "marksman":
            return {
                "label": "proteção de carry com tempo de objetivo",
                "plan": f"{jungle.name} com {lane.name} quer garantir entrada limpa no rio e fight longa com front line viva.",
                "spike": "a sinergia cresce quando o primeiro item do carry chega e o jungler já tem recurso para abrir espaço.",
                "champions": [jungle.name, lane.name],
            }
        return None

    def _normalize_role(self, role: Any) -> str:
        token = str(role or "").strip().lower().replace(" ", "_")
        aliases = {
            "adc": "bottom",
            "bot": "bottom",
            "botlane": "bottom",
            "bottom_lane": "bottom",
            "bottom": "bottom",
            "support": "support",
            "sup": "support",
            "utility": "support",
            "mid": "mid",
            "middle": "mid",
            "top": "top",
            "jungle": "jungle",
            "jg": "jungle",
        }
        return aliases.get(token, token)

    def _draft_candidate_pool(self, role: str | None = None) -> list[str]:
        desired_role = self._normalize_role(role or "")
        champions = self._overrides.get("champions", {})
        candidates = []

        for champion_key, champion_override in champions.items():
            champion = self.get_champion(champion_key)
            champion_name = champion.name if champion else None
            if not champion_name:
                continue
            roles = set((champion_override.get("roles") or {}).keys())
            if desired_role:
                if desired_role in roles:
                    candidates.append(champion_name)
            elif roles:
                candidates.append(champion_name)

        if candidates:
            return sorted(dict.fromkeys(candidates))

        fallback = {
            "top": ["Aatrox", "Camille", "Darius", "Fiora", "Garen", "Malphite", "Ornn", "Renekton"],
            "jungle": ["Jarvan IV", "Lee Sin", "Nocturne", "Sejuani", "Vi", "Viego", "Wukong", "Xin Zhao"],
            "mid": ["Ahri", "Azir", "Orianna", "Sylas", "Syndra", "Taliyah", "Viktor", "Yone"],
            "bottom": ["Caitlyn", "Draven", "Jinx", "KaiSa", "Lucian", "Xayah"],
            "support": ["Leona", "Lulu", "Milio", "Nami", "Nautilus", "Rakan", "Thresh"],
        }
        if desired_role in fallback:
            return fallback[desired_role]
        return sorted(
            {
                champion
                for pool in fallback.values()
                for champion in pool
            }
        )

    def _draft_ban_candidate_pool(
        self,
        role: str | None,
        enemy_profiles: list[ChampionKnowledge] | None = None,
        current_pick: ChampionKnowledge | None = None,
        revealed_enemies: list[dict[str, Any]] | None = None,
    ) -> list[str]:
        desired_role = self._normalize_role(role or "")
        candidates = list(_ROLE_BAN_POOL.get(desired_role, []))

        if desired_role == "top":
            candidates.extend(["Aatrox", "Camille", "Fiora", "Ornn", "Renekton"])
        elif desired_role == "mid":
            candidates.extend(["Ahri", "Syndra", "Viktor", "Yone", "Zed", "Akali", "Sylas"])
        elif desired_role == "bottom":
            candidates.extend(["Caitlyn", "Draven", "Jinx", "Leona", "Nautilus"])
        elif desired_role == "support":
            candidates.extend(["Leona", "Nautilus", "Thresh", "Lulu", "Nami", "Milio"])

        if current_pick:
            candidates.append(current_pick.name)

        for enemy in revealed_enemies or []:
            enemy_name = (enemy or {}).get("champion")
            enemy_role = self._normalize_role((enemy or {}).get("role") or "")
            enemy_profile = self.get_champion(enemy_name)
            if not enemy_profile:
                continue
            if enemy_role == "support":
                if enemy_profile.archetype in {"engage_support", "tank"}:
                    candidates.extend(["Draven", "Samira", "Kalista", "Miss Fortune"])
                elif enemy_profile.archetype == "enchanter":
                    candidates.extend(["Jinx", "Kog'Maw", "Zeri", "Twitch"])
                elif enemy_profile.archetype == "poke_support":
                    candidates.extend(["Caitlyn", "Varus", "Ashe"])
            elif enemy_role == "bottom":
                if enemy_profile.name in {"Draven", "Samira", "Kalista"}:
                    candidates.extend(["Leona", "Nautilus", "Rell"])
                elif enemy_profile.name in {"Jinx", "Kog'Maw", "Zeri", "Twitch"}:
                    candidates.extend(["Lulu", "Milio", "Nami"])
                elif enemy_profile.name in {"Caitlyn", "Varus", "Ashe"}:
                    candidates.extend(["Lux", "Zyra", "Karma", "Nami"])
            elif enemy_role == "mid":
                if enemy_profile.archetype == "assassin":
                    candidates.extend(["Jarvan IV", "Vi", "Nocturne"])
                elif enemy_profile.archetype in {"control_mage", "burst_mage"}:
                    candidates.extend(["Sejuani", "Wukong", "Lee Sin"])

        for enemy in enemy_profiles or []:
            candidates.append(enemy.name)
            if enemy.archetype == "assassin":
                candidates.extend(["Akali", "LeBlanc", "Zed", "Yone"])
            elif enemy.archetype == "control_mage":
                candidates.extend(["Ahri", "Azir", "Orianna", "Syndra", "Viktor"])
            elif enemy.archetype == "marksman":
                candidates.extend(["Caitlyn", "Draven", "Jinx", "Kai'Sa", "Lucian"])
            elif enemy.archetype == "engage_support":
                candidates.extend(["Leona", "Nautilus", "Rell", "Thresh"])
            elif enemy.archetype in {"juggernaut", "skirmisher"}:
                candidates.extend(["Aatrox", "Camille", "Fiora", "Renekton", "Yone"])

        available = []
        seen = set()
        for candidate_name in candidates:
            champion = self.get_champion(candidate_name)
            if not champion:
                continue
            normalized_name = _normalize_name(champion.name)
            if normalized_name in seen:
                continue
            seen.add(normalized_name)
            available.append(champion.name)
        return available

    def _score_pick_candidate(
        self,
        candidate: ChampionKnowledge,
        enemy_profiles: list[ChampionKnowledge],
        threats: dict[str, int],
        *,
        role: str | None = None,
        allies: list[dict[str, Any]] | None = None,
        revealed_enemies: list[dict[str, Any]] | None = None,
        draft_window: dict[str, Any] | None = None,
    ) -> tuple[float, list[str]]:
        score = 50.0
        reasons: list[str] = []
        role_key = self._normalize_role(role or "")

        archetype = candidate.archetype
        if threats["tank"] >= 2 and archetype in {"marksman", "control_mage", "bruiser", "skirmisher"}:
            score += 7
            reasons.append("responde melhor a front line pesada")
        if threats["assassin"] >= 2 and archetype in {"tank", "engage_support", "enchanter", "control_mage"}:
            score += 6
            reasons.append("segura melhor comp de pick e burst")
        if threats["poke"] >= 3 and archetype in {"engage_support", "assassin", "tank", "bruiser"}:
            score += 5
            reasons.append("encurta a luta contra comp de poke")
        if threats["hard_cc"] >= 2 and archetype in {"marksman", "control_mage", "burst_mage"}:
            score -= 3
        if threats["engage"] >= 2 and archetype in {"tank", "engage_support", "bruiser", "skirmisher"}:
            score += 4
            reasons.append("aguenta melhor engage reto")

        for enemy in enemy_profiles:
            insight = self.get_lane_matchup_insight(candidate.name, enemy.name, role=role_key)
            if not insight:
                continue
            verdict = str(insight.get("verdict", "")).strip().lower()
            if verdict in {"favoravel", "favoravel se entrares bem", "pressionavel", "escalavel"}:
                score += 2.5
            elif verdict in {"skill", "explosivo"}:
                score += 0.5
            elif verdict in {"perigoso", "delicado", "all-in ou nada"}:
                score -= 2

        direct_enemy = next(
            (
                self.get_champion((enemy or {}).get("champion"))
                for enemy in (revealed_enemies or [])
                if self._normalize_role((enemy or {}).get("role") or "") == role_key
                and (enemy or {}).get("champion")
            ),
            None,
        )
        if direct_enemy:
            direct_insight = self.get_lane_matchup_insight(candidate.name, direct_enemy.name, role=role_key) or {}
            direct_verdict = str(direct_insight.get("verdict", "")).strip().lower()
            if direct_verdict in {"favoravel", "favoravel se entrares bem", "pressionavel", "escalavel"}:
                score += 6
                reasons.insert(0, f"countera direto o pick revelado de {direct_enemy.name} na tua rota")
            elif direct_verdict in {"skill", "explosivo"}:
                score += 2
                reasons.insert(0, f"segura bem o pick revelado de {direct_enemy.name} na tua rota")

        if allies:
            if self._resolve_duo_bonus(candidate.name, role_key, allies):
                score += 4
                reasons.append("tem sinergia boa com teu aliado direto")
            if self._resolve_jungle_bonus(candidate.name, role_key, allies):
                score += 3
                reasons.append("conversa bem com o plano do jungler")

        guidance = self.get_draft_guidance(candidate.name, [enemy.name for enemy in enemy_profiles], role=role_key) or {}
        for focus in guidance.get("build_focus", [])[:2]:
            normalized_focus = str(focus or "").strip()
            if normalized_focus:
                reasons.append(normalized_focus)

        return score, reasons[:3]

    def _adjust_pick_for_draft_window(
        self,
        score: float,
        reasons: list[str],
        *,
        role: str | None = None,
        familiarity: str,
        draft_window: dict[str, Any] | None = None,
        enemy_anchor: Any | None = None,
    ) -> tuple[float, list[str]]:
        window = draft_window or {}
        role_key = self._normalize_role(role or "")
        response_risk = str(window.get("response_risk") or "low").strip().lower()
        draft_open = bool(window.get("draft_open"))
        lane_state = str(window.get("lane_state") or "hidden").strip().lower()
        lane_response_state = str(window.get("lane_response_state") or "blind").strip().lower()
        revealed_lane_roles = {
            self._normalize_role(value or "")
            for value in (window.get("revealed_lane_roles") or [])
        }
        selection_posture = str(window.get("selection_posture") or "neutral").strip().lower()
        rotation_stage = str(window.get("rotation_stage") or "unknown").strip().lower()
        info_edge = str(window.get("info_edge") or "even").strip().lower()
        team_side = str(window.get("team_side") or "blue").strip().lower()
        ally_slot_timing = str(window.get("ally_slot_timing") or "solo").strip().lower()
        ally_locked_count = int(window.get("ally_locked_count") or 0)
        enemy_locked_count = int(window.get("enemy_locked_count") or 0)

        updated_reasons = list(reasons)
        if response_risk == "high":
            if familiarity in {"main", "pool"}:
                score += 4
                updated_reasons.insert(0, "a draft ainda pode responder tua rota, entao conforto pesa mais agora")
            elif familiarity == "off_pool":
                score -= 4
                updated_reasons.append("ainda pode tomar resposta depois, entao esse pick pede mais cuidado")
        elif response_risk == "medium":
            if familiarity in {"main", "pool"}:
                score += 2
            elif familiarity == "off_pool" and draft_open:
                score -= 2
        elif response_risk == "low" and enemy_anchor and familiarity == "off_pool":
            score += 2
            updated_reasons.append("a lane ja esta mais desenhada, entao o counter teorico ganha valor")

        if lane_state == "partial":
            if familiarity in {"main", "pool"}:
                score += 2
                updated_reasons.insert(0, "so metade da lane apareceu, entao conforto seguro vale mais por enquanto")
            elif familiarity == "off_pool":
                score -= 2
                updated_reasons.append("a lane ainda nao mostrou tudo, entao esse counter pode ficar mais punivel")
        elif lane_state == "full" and enemy_anchor and familiarity == "off_pool":
            score += 2
            updated_reasons.append("a lane inimiga ja esta praticamente fechada, entao o counter ganha mais valor agora")

        if lane_response_state == "semi":
            if familiarity in {"main", "pool"}:
                score += 1
                updated_reasons.insert(0, "tua rota ja comecou a responder, mas ainda nao fechou o suficiente pra largar estabilidade")
            elif familiarity == "off_pool":
                score -= 1
                updated_reasons.append("ja existe uma resposta parcial na rota, mas ainda nao da pra se vender demais no counter")
        elif lane_response_state == "answered" and enemy_anchor and familiarity == "off_pool":
            score += 1
            updated_reasons.append("a tua rota ja esta bem respondida, entao da pra apertar um pouco mais o matchup")

        if role_key in {"top", "mid", "middle"}:
            precise_answer_window = (
                selection_posture == "answer"
                and lane_response_state == "answered"
                and response_risk == "low"
            )
            if team_side == "blue" and ally_slot_timing == "early":
                if familiarity in {"main", "pool"}:
                    score += 1
                    updated_reasons.insert(0, "lado azul cedo costuma pedir blind mais estavel do que pick de luxo")
                elif familiarity == "off_pool":
                    score -= 1
            elif team_side == "red" and ally_slot_timing == "late" and enemy_anchor and familiarity == "off_pool":
                score += 1
                updated_reasons.append("lado vermelho mais tarde te libera responder a lane com mais precisao")

            if info_edge == "exposed":
                if familiarity in {"main", "pool"}:
                    score += 2
                    updated_reasons.insert(0, "teu lado ja mostrou mais coisa, entao conforto e estabilidade sobem de valor")
                elif familiarity == "off_pool":
                    score -= 2
            elif info_edge == "answering" and enemy_anchor and familiarity == "off_pool":
                score += 2
                updated_reasons.append("teu lado esta respondendo com mais informacao, entao o counter direto fica melhor")

            if rotation_stage == "first":
                if familiarity in {"main", "pool"}:
                    score += 1
                    updated_reasons.insert(0, "primeira rotacao pede mais estabilidade do que hero pick")
                elif familiarity == "off_pool":
                    score -= 2
            elif rotation_stage in {"second", "late"} and enemy_anchor and familiarity == "off_pool":
                score += 1

            if selection_posture == "blind":
                if familiarity in {"main", "pool"}:
                    score += 2
                    updated_reasons.insert(0, "teu slot aqui e blind, entao estabilidade vale mais que pick bonito no papel")
                elif familiarity == "off_pool":
                    score -= 3
                    updated_reasons.append("esse pick entra muito exposto se tu tiver que blindar a rota")
            elif selection_posture == "answer" and enemy_anchor and familiarity == "off_pool":
                score += 3
                updated_reasons.append("teu slot aqui ja responde mais do que blinda, entao o counter direto ganha muito valor")
            elif selection_posture == "contest" and familiarity in {"main", "pool"}:
                score += 1
                updated_reasons.insert(0, "essa janela ainda e de contestacao, entao conforto consistente continua valendo")

            if precise_answer_window:
                if familiarity == "off_pool":
                    score += 4
                    updated_reasons.append("a solo lane ja esta aberta o bastante para premiar resposta mais cirurgica")
                elif familiarity == "main":
                    score -= 2
                elif familiarity == "pool":
                    score -= 1

            if lane_state == "hidden" and response_risk == "high":
                if familiarity in {"main", "pool"}:
                    score += 2
                    updated_reasons.insert(0, "isso ainda esta bem blind na tua rota, entao conforto pesa mais do que teoria")
                elif familiarity == "off_pool":
                    score -= 3
                    updated_reasons.append("blind pick muito ambicioso nessa rota ainda pode virar counter facil")
            elif lane_state == "full" and enemy_anchor and familiarity == "off_pool":
                score += 2
                updated_reasons.append("o counter da tua rota ja esta mais exposto, entao da pra apertar mais o matchup")

        if role_key in {"bottom", "support"}:
            if revealed_lane_roles == {"bottom"}:
                if familiarity in {"main", "pool"}:
                    score += 1
                    updated_reasons.insert(0, "so o adc deles apareceu, entao ainda vale mais respeitar o que falta fechar da dupla")
                elif familiarity == "off_pool":
                    score -= 1
            elif revealed_lane_roles == {"support"}:
                if familiarity in {"main", "pool"}:
                    score += 1
                    updated_reasons.insert(0, "so o suporte deles apareceu, entao ainda nao e hora de vender demais a lane no papel")
                elif familiarity == "off_pool":
                    score -= 1
            if lane_response_state == "answered" and enemy_anchor and familiarity == "off_pool":
                score += 1
                updated_reasons.append("a dupla ja esta quase toda resolvida, entao o counter da bot lane sobe de valor")

        if role_key == "jungle":
            total_locked = ally_locked_count + enemy_locked_count
            if total_locked <= 2:
                if familiarity in {"main", "pool"}:
                    score += 1
                    updated_reasons.insert(0, "o mapa ainda esta muito cego, entao jungle segura vale mais que inventar moda")
            elif total_locked <= 5:
                if familiarity in {"main", "pool"}:
                    score += 1
                    updated_reasons.append("o mapa ja comecou a desenhar, mas ainda pede consistencia")
            elif familiarity == "off_pool":
                score += 1
                updated_reasons.append("com o mapa mais respondido, da pra apertar mais a leitura da jungle")
            if team_side == "blue" and ally_slot_timing == "early" and familiarity in {"main", "pool"}:
                score += 1
            elif team_side == "red" and ally_slot_timing == "late" and familiarity == "off_pool":
                score += 1
            if info_edge == "answering" and familiarity == "off_pool":
                score += 1
            elif info_edge == "exposed" and familiarity in {"main", "pool"}:
                score += 1
            if response_risk == "high" and familiarity == "off_pool":
                score += 1
            if familiarity in {"main", "pool"} and draft_open:
                score += 1
            if rotation_stage in {"second", "late"} and familiarity == "off_pool":
                score += 1
            updated_reasons = [
                reason for reason in updated_reasons
                if "tua rota" not in str(reason or "").lower()
            ]
            if draft_open:
                updated_reasons.append("na jungle a draft pesa mais por mapa e comp do que por duelo direto de lane")

        deduped: list[str] = []
        seen = set()
        for reason in updated_reasons:
            key = str(reason or "").strip().lower()
            if not key or key in seen:
                continue
            seen.add(key)
            deduped.append(reason)
        return score, deduped[:3]

    def _classify_ban_context(
        self,
        *,
        role: str | None = None,
        revealed_enemies: list[dict[str, Any]] | None = None,
    ) -> str:
        role_key = self._normalize_role(role or "")
        revealed_roles = {
            self._normalize_role((enemy or {}).get("role") or "")
            for enemy in (revealed_enemies or [])
            if (enemy or {}).get("champion")
        }
        if role_key in {"bottom", "support"} and {"bottom", "support"} <= revealed_roles:
            return "duo-forming"
        if role_key in revealed_roles:
            return "role-revealed"
        return "comp-read"

    def _classify_pick_focus(
        self,
        reasons: list[str] | tuple[str, ...],
        *,
        familiarity: str = "off_pool",
        role: str | None = None,
    ) -> str:
        if familiarity in {"main", "pool"}:
            return "comfort-pick"
        normalized_reasons = " | ".join(str(reason or "").strip().lower() for reason in reasons if reason).strip()
        if "lane" in normalized_reasons or "engage" in normalized_reasons or "burst" in normalized_reasons:
            return "anti-lane"
        if "front line" in normalized_reasons or "poke" in normalized_reasons or "comp" in normalized_reasons or "jungler" in normalized_reasons:
            return "anti-comp"
        role_key = self._normalize_role(role or "")
        if role_key in {"bottom", "support"}:
            return "anti-lane"
        return "anti-comp"

    def _classify_pick_context(
        self,
        *,
        role: str | None = None,
        revealed_enemies: list[dict[str, Any]] | None = None,
        enemy_anchor: Any | None = None,
    ) -> str:
        role_key = self._normalize_role(role or "")
        if enemy_anchor:
            return "lane-revealed"
        if role_key in {"bottom", "support"}:
            revealed_roles = {
                self._normalize_role((enemy or {}).get("role") or "")
                for enemy in (revealed_enemies or [])
                if (enemy or {}).get("champion")
            }
            if {"bottom", "support"} <= revealed_roles:
                return "duo-forming"
        if any(
            self._normalize_role((enemy or {}).get("role") or "") == role_key
            for enemy in (revealed_enemies or [])
        ):
            return "role-revealed"
        return "comp-read"

    def _classify_pick_window(
        self,
        *,
        draft_window: dict[str, Any] | None = None,
        familiarity: str = "off_pool",
        enemy_anchor: Any | None = None,
        role: str | None = None,
    ) -> str:
        role_key = self._normalize_role(role or "")
        risk = str((draft_window or {}).get("response_risk") or "low").strip().lower()
        lane_state = str((draft_window or {}).get("lane_state") or "hidden").strip().lower()
        lane_response_state = str((draft_window or {}).get("lane_response_state") or "blind").strip().lower()
        revealed_lane_roles = {
            self._normalize_role(value or "")
            for value in ((draft_window or {}).get("revealed_lane_roles") or [])
        }
        posture = str((draft_window or {}).get("selection_posture") or "neutral").strip().lower()
        info_edge = str((draft_window or {}).get("info_edge") or "even").strip().lower()
        team_side = str((draft_window or {}).get("team_side") or "blue").strip().lower()
        ally_slot_timing = str((draft_window or {}).get("ally_slot_timing") or "solo").strip().lower()
        ally_locked_count = int((draft_window or {}).get("ally_locked_count") or 0)
        enemy_locked_count = int((draft_window or {}).get("enemy_locked_count") or 0)
        if posture == "blind":
            return "blind-slot"
        if posture == "answer":
            return "answer-slot"
        if posture == "contest":
            return "contest-slot"
        if role_key in {"bottom", "support"}:
            if revealed_lane_roles == {"bottom"}:
                return "adc-revealed"
            if revealed_lane_roles == {"support"}:
                return "support-revealed"
            if lane_response_state == "answered":
                return "duo-answered"
        if role_key == "jungle":
            total_locked = ally_locked_count + enemy_locked_count
            if total_locked <= 2:
                return "map-blind"
            if total_locked <= 5:
                return "map-semi"
            return "map-answered"
        if lane_response_state == "semi":
            return "lane-semi"
        if lane_response_state == "answered":
            return "lane-answered"
        if lane_state == "partial":
            return "lane-partial"
        if lane_state == "full":
            return "lane-complete"
        if team_side == "blue" and ally_slot_timing == "early" and familiarity in {"main", "pool"} and risk in {"medium", "high"}:
            return "blue-open"
        if team_side == "red" and ally_slot_timing == "late" and (
            (enemy_anchor and familiarity == "off_pool")
            or info_edge == "answering"
        ):
            return "red-answer"
        if info_edge == "exposed" and familiarity in {"main", "pool"} and risk in {"medium", "high"}:
            return "info-exposed"
        if info_edge == "answering" and (
            (enemy_anchor and familiarity == "off_pool")
            or role_key == "jungle"
        ):
            return "info-answering"
        if risk == "high":
            return "response-open" if familiarity == "off_pool" else "comfort-window"
        if risk == "medium":
            return "draft-open"
        if enemy_anchor:
            return "lane-shaped"
        return "draft-shaped"

    def _adjust_ban_for_draft_window(
        self,
        score: float,
        reasons: list[str],
        *,
        role: str | None = None,
        current_pick: ChampionKnowledge | None = None,
        draft_window: dict[str, Any] | None = None,
    ) -> tuple[float, list[str]]:
        window = draft_window or {}
        role_key = self._normalize_role(role or "")
        response_risk = str(window.get("response_risk") or "low").strip().lower()
        lane_state = str(window.get("lane_state") or "hidden").strip().lower()
        lane_response_state = str(window.get("lane_response_state") or "blind").strip().lower()
        revealed_lane_roles = {
            self._normalize_role(value or "")
            for value in (window.get("revealed_lane_roles") or [])
        }
        selection_posture = str(window.get("selection_posture") or "neutral").strip().lower()
        rotation_stage = str(window.get("rotation_stage") or "unknown").strip().lower()
        info_edge = str(window.get("info_edge") or "even").strip().lower()
        team_side = str(window.get("team_side") or "blue").strip().lower()
        ally_slot_timing = str(window.get("ally_slot_timing") or "solo").strip().lower()
        ally_locked_count = int(window.get("ally_locked_count") or 0)
        enemy_locked_count = int(window.get("enemy_locked_count") or 0)

        updated_reasons = list(reasons)

        if role_key in {"top", "mid", "middle"}:
            if team_side == "blue" and ally_slot_timing == "early":
                score += 1
                updated_reasons.insert(0, "lado azul cedo pede ban mais estavel para proteger o blind da rota")
            elif team_side == "red" and ally_slot_timing == "late" and current_pick:
                score += 1
                updated_reasons.append("lado vermelho mais tarde te libera um ban bem mais cirurgico")
            if info_edge == "exposed":
                score += 1
                updated_reasons.insert(0, "teu lado ja mostrou mais da draft, entao o ban precisa proteger melhor a rota")
            elif info_edge == "answering" and current_pick:
                score += 1
                updated_reasons.append("teu lado esta respondendo com mais informacao, entao o ban pode ser mais cirurgico")
            if rotation_stage == "first":
                score += 1
                updated_reasons.insert(0, "primeira rotacao costuma pedir ban mais seguro e menos ganancioso")
            elif rotation_stage in {"second", "late"} and current_pick:
                score += 1
                updated_reasons.append("rotacao mais tardia libera um ban mais cirurgico")
            if current_pick and selection_posture == "blind":
                score += 2
                updated_reasons.insert(0, "teu slot entrou mais cego, entao esse ban protege melhor a solo lane")
            elif current_pick and selection_posture == "answer":
                score += 1
                updated_reasons.append("como teu slot ja respondeu mais do que blindou, o ban pode ser mais cirurgico")
            if current_pick and response_risk == "high":
                score += 2
                updated_reasons.insert(0, "a tua solo lane ainda esta blind o bastante para pedir protecao antes de ganancia")
            elif current_pick and lane_state == "full":
                score += 2
                updated_reasons.append("a rota ja apareceu direito, entao o ban pode ficar mais cirurgico")
            elif not current_pick and response_risk == "high":
                score += 2
                updated_reasons.append("esse corte segura melhor o blind da solo lane antes dela abrir torta")

        elif role_key in {"bottom", "support"}:
            if team_side == "blue" and ally_slot_timing == "early" and lane_state != "full":
                score += 1
                updated_reasons.append("lado azul cedo no bot pede corte mais seguro antes da dupla fechar")
            elif team_side == "red" and ally_slot_timing == "late" and lane_state == "full":
                score += 1
                updated_reasons.append("lado vermelho mais tarde no bot libera um corte mais cirurgico da dupla")
            if revealed_lane_roles == {"bottom"}:
                score += 1
                updated_reasons.append("so o adc apareceu, entao o corte ainda precisa respeitar o suporte que falta fechar")
            elif revealed_lane_roles == {"support"}:
                score += 1
                updated_reasons.append("so o suporte apareceu, entao o ban ainda segura bem a parte oculta da lane")
            if info_edge == "exposed" and lane_state != "full":
                score += 1
                updated_reasons.append("teu lado mostrou mais cedo, entao vale segurar melhor a pressao da lane")
            if lane_response_state == "semi":
                score += 1
                updated_reasons.append("a rota ja comecou a responder, mas ainda nao fechou o bastante para largar seguranca")
            elif lane_response_state == "answered":
                score += 1
                updated_reasons.append("a rota ja esta bem respondida, entao o ban pode cortar a dupla com mais precisao")
            if lane_state == "partial":
                score += 3
                updated_reasons.insert(0, "so metade da bot lane apareceu, entao esse ban segura bem o desconhecido")
            elif lane_state == "full":
                score += 2
                updated_reasons.append("a dupla inimiga ja esta mais exposta, entao o ban pode quebrar melhor a lane")
            if rotation_stage == "first" and lane_state != "full":
                score += 1
                updated_reasons.append("na primeira rotacao, cortar pressao geral da lane costuma render mais")

        elif role_key == "jungle":
            total_locked = ally_locked_count + enemy_locked_count
            updated_reasons = [
                reason for reason in updated_reasons
                if "lane" not in str(reason or "").lower()
            ]
            if total_locked <= 2:
                score += 1
                updated_reasons.append("o mapa ainda esta cego, entao a jungle pede corte de estrutura mais seguro")
            elif total_locked <= 5:
                score += 1
                updated_reasons.append("o mapa ja esta semi-desenhado, entao o corte pode mirar engage e ritmo")
            else:
                score += 1
                updated_reasons.append("com o mapa mais respondido, o ban pode mirar leitura mais precisa da jungle")
            if team_side == "blue" and ally_slot_timing == "early":
                score += 1
                updated_reasons.append("lado azul cedo na jungle costuma pedir corte seguro de estrutura")
            elif team_side == "red" and ally_slot_timing == "late":
                score += 1
                updated_reasons.append("lado vermelho mais tarde na jungle libera um corte mais preciso de mapa")
            if info_edge == "answering":
                score += 1
                updated_reasons.append("com mais informacao do mapa na mesa, o ban pode mirar melhor a estrutura inimiga")
            if response_risk == "high":
                score += 2
                updated_reasons.insert(0, "na jungle o corte vale mais por mapa, engage e estrutura da comp")
            elif lane_state == "full":
                score += 1
                updated_reasons.append("com as lanes mais expostas, o ban fica mais sobre mapa do que surpresa")
            if rotation_stage == "first":
                score += 1
                updated_reasons.append("cedo na draft, jungle prefere corte de estrutura antes de corte de lane")

        deduped: list[str] = []
        seen = set()
        for reason in updated_reasons:
            key = str(reason or "").strip().lower()
            if not key or key in seen:
                continue
            seen.add(key)
            deduped.append(reason)
        return score, deduped[:3]

    def _score_ban_candidate(
        self,
        candidate: ChampionKnowledge,
        enemy_profiles: list[ChampionKnowledge],
        *,
        role: str | None = None,
        stage: str = "ban",
        current_pick: ChampionKnowledge | None = None,
        revealed_enemies: list[dict[str, Any]] | None = None,
        draft_window: dict[str, Any] | None = None,
        preferred_pool: list[ChampionKnowledge] | None = None,
    ) -> tuple[float, list[str]]:
        score = 35.0
        reasons: list[str] = []
        role_key = self._normalize_role(role or "")
        stage_key = str(stage or "ban").strip().lower()
        response_risk = str((draft_window or {}).get("response_risk") or "low").strip().lower()
        enemy_support_profile: ChampionKnowledge | None = None
        enemy_bottom_profile: ChampionKnowledge | None = None
        solo_lane_candidate_names: set[str] = set()
        if role_key in {"top", "mid", "middle"}:
            canonical_role = "mid" if role_key == "middle" else role_key
            solo_lane_candidate_names = set(_ROLE_BAN_POOL.get(canonical_role, []))
            if canonical_role == "top":
                solo_lane_candidate_names.update({"Aatrox", "Camille", "Fiora", "Ornn", "Renekton"})
            elif canonical_role == "mid":
                solo_lane_candidate_names.update({"Ahri", "Syndra", "Viktor", "Yone", "Zed", "Akali", "Sylas"})
        is_solo_lane_candidate = not solo_lane_candidate_names or candidate.name in solo_lane_candidate_names

        if current_pick and role_key != "jungle" and is_solo_lane_candidate:
            insight = self.get_lane_matchup_insight(current_pick.name, candidate.name, role=role_key) or {}
            verdict = str(insight.get("verdict", "")).strip().lower()
            danger = str(insight.get("danger", "")).strip()
            if verdict in {"perigoso", "delicado", "all-in ou nada"}:
                score += 11 if stage_key == "ban" else 16
                reasons.append(f"te pune direto se vier de {candidate.name}")
            elif verdict in {"explosivo", "skill"}:
                score += 4 if stage_key == "ban" else 8
                reasons.append(f"pode deixar a lane instavel contra teu {current_pick.name}")
            if danger:
                reasons.append(danger)

        pool_hits = 0
        main_style_hits = 0
        for pool_champion in preferred_pool or []:
            if role_key == "jungle":
                break
            if role_key in {"top", "mid", "middle"} and not is_solo_lane_candidate:
                break
            insight = self.get_lane_matchup_insight(pool_champion.name, candidate.name, role=role_key) or {}
            verdict = str(insight.get("verdict", "")).strip().lower()
            if verdict in {"perigoso", "delicado", "all-in ou nada", "explosivo"}:
                pool_hits += 1
                if verdict in {"perigoso", "delicado", "all-in ou nada"}:
                    main_style_hits += 1
        if pool_hits:
            score += pool_hits * (3 if stage_key == "ban" else 4)
            reasons.insert(0, f"incomoda {pool_hits} campeoes da tua pool")
        if main_style_hits >= 2:
            score += 3 if stage_key == "ban" else 5
            reasons.insert(0, "atrapalha teu conforto com mais consistencia")
        if current_pick and response_risk == "high":
            score += 3
            reasons.insert(0, "te protege melhor porque a draft ainda consegue responder teu pick")
        elif current_pick and response_risk == "low":
            score -= 1

        for enemy in revealed_enemies or []:
            enemy_name = (enemy or {}).get("champion")
            enemy_role = self._normalize_role((enemy or {}).get("role") or "")
            enemy_profile = self.get_champion(enemy_name)
            if not enemy_profile:
                continue
            if enemy_role == "support":
                enemy_support_profile = enemy_profile
            elif enemy_role == "bottom":
                enemy_bottom_profile = enemy_profile
            if role_key in {"bottom", "support"}:
                if enemy_role == "support":
                    if enemy_profile.archetype in {"engage_support", "tank"} and candidate.name in {"Draven", "Samira", "Kalista", "Miss Fortune"}:
                        score += 4
                        reasons.append("quebra a dupla agressiva que esse suporte revelado quer montar")
                    elif enemy_profile.archetype == "enchanter" and candidate.name in {"Jinx", "Kog'Maw", "Zeri", "Twitch"}:
                        score += 4
                        reasons.append("corta o carry que mais escala com esse suporte revelado")
                elif enemy_role == "bottom":
                    if enemy_profile.name in {"Draven", "Samira", "Kalista"} and candidate.name in {"Leona", "Nautilus", "Rell"}:
                        score += 4
                        reasons.append("quebra o suporte que mais completa esse ADC revelado")
                    elif enemy_profile.name in {"Jinx", "Kog'Maw", "Zeri", "Twitch"} and candidate.name in {"Lulu", "Milio", "Nami"}:
                        score += 4
                        reasons.append("corta o suporte que mais habilita esse carry revelado")

        projected_threats = self._threat_counts([*enemy_profiles, candidate])
        if candidate.name in _HARD_CC_CHAMPS and projected_threats["hard_cc"] >= 3:
            score += 4
            reasons.append("fecha uma draft chata de controle")
        if candidate.archetype == "assassin" and projected_threats["assassin"] >= 2:
            score += 3
            reasons.append("empilha burst e pickoff do lado deles")
        if candidate.archetype in {"tank", "juggernaut"} and projected_threats["tank"] >= 2:
            score += 3
            reasons.append("engrossa demais a front line inimiga")
        if candidate.name in _SUSTAIN_CHAMPS and projected_threats["sustain"] >= 2:
            score += 2
            reasons.append("obriga tua comp a responder cura cedo")
        if stage_key == "ban" and not current_pick:
            if role_key == "top" and candidate.archetype in {"juggernaut", "skirmisher"}:
                score += 4
                reasons.append("tira uma lane de side muito chata da mesa")
            elif role_key == "mid" and candidate.archetype in {"assassin", "control_mage"}:
                score += 4
                reasons.append("evita draft de mid que distorce tua lane cedo")
            elif role_key == "bottom" and candidate.archetype == "marksman":
                score += 4
                reasons.append("limpa um carry de bot que escala ou pressiona demais")
            elif role_key == "support" and candidate.archetype in {"engage_support", "enchanter"}:
                score += 4
                reasons.append("corta um suporte que muda demais o ritmo da lane")
        if role_key == "bottom":
            if candidate.name in {"Caitlyn", "Draven"}:
                score += 3
                reasons.append("pode distorcer a lane cedo demais")
            if candidate.name in {"Leona", "Nautilus", "Thresh"}:
                score += 2
                reasons.append("pune muito posicionamento ruim no bot")
        elif role_key == "support":
            support_lane_response_state = str(
                (draft_window or {}).get("lane_response_state") or "blind"
            ).strip().lower()
            if candidate.name in {"Lulu", "Nami", "Milio"}:
                score += 2
                reasons.append("protege demais o carry se passar")
            if candidate.name in {"Leona", "Nautilus", "Thresh", "Rell"}:
                score += 3
                reasons.append("dita a engage da lane quase sozinho")
            engage_support_revealed = bool(
                enemy_support_profile
                and enemy_support_profile.archetype in {"engage_support", "tank"}
            )
            aggressive_adc_revealed = bool(
                enemy_bottom_profile
                and enemy_bottom_profile.name in _AGGRESSIVE_BOT_CARRIES
            )
            scaling_adc_revealed = bool(
                enemy_bottom_profile
                and enemy_bottom_profile.name in _HYPER_SCALING_BOT_CARRIES
            )
            if engage_support_revealed and aggressive_adc_revealed:
                if candidate.name in {"Leona", "Nautilus", "Rell", "Thresh", "Blitzcrank", "Pyke"}:
                    score += 5
                    reasons.insert(0, "quebra melhor a dupla explosiva que eles ja mostraram no bot")
                elif candidate.archetype == "poke_support":
                    score -= 3
                elif candidate.archetype == "enchanter":
                    score -= 1
            elif engage_support_revealed and support_lane_response_state in {"semi", "answered"}:
                if candidate.name in {"Leona", "Nautilus", "Rell", "Thresh", "Blitzcrank"}:
                    score += 3
                    reasons.insert(0, "segura melhor a lane de engage que eles estao montando")
                elif candidate.archetype == "poke_support":
                    score -= 2
            if scaling_adc_revealed and enemy_support_profile and enemy_support_profile.archetype == "enchanter":
                if candidate.name in {"Lulu", "Milio", "Nami", "Yuumi"}:
                    score += 3
                    reasons.insert(0, "corta o suporte que mais libera esse carry para escalar limpo")
        elif role_key == "mid":
            if candidate.name in {"Zed", "Akali", "Yone", "LeBlanc"}:
                score += 3
                reasons.append("pode explodir a lane no primeiro all-in real")
            if candidate.name in {"Syndra", "Orianna", "Viktor", "Azir"}:
                score += 2
                reasons.append("controla demais a wave e o espaço do mid")
        elif role_key == "top":
            if candidate.name in {"Fiora", "Camille", "Aatrox", "Renekton"}:
                score += 3
                reasons.append("pode transformar o top numa side muito difícil")
            if candidate.name in {"Ornn", "Malphite"}:
                score += 2
                reasons.append("escala bem demais se a lane ficar limpa")

        if role_key in {"top", "mid", "middle"} and current_pick and not is_solo_lane_candidate:
            if response_risk == "low":
                score -= 12
            else:
                score -= 4

        seen = set()
        unique_reasons = []
        for reason in reasons:
            normalized = str(reason or "").strip().lower()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            unique_reasons.append(reason)
        return score, unique_reasons[:3]

    def _classify_ban_window(
        self,
        *,
        role: str | None = None,
        draft_window: dict[str, Any] | None = None,
        current_pick: ChampionKnowledge | None = None,
    ) -> str:
        role_key = self._normalize_role(role or "")
        risk = str((draft_window or {}).get("response_risk") or "low").strip().lower()
        lane_state = str((draft_window or {}).get("lane_state") or "hidden").strip().lower()
        lane_response_state = str((draft_window or {}).get("lane_response_state") or "blind").strip().lower()
        revealed_lane_roles = {
            self._normalize_role(value or "")
            for value in ((draft_window or {}).get("revealed_lane_roles") or [])
        }
        posture = str((draft_window or {}).get("selection_posture") or "neutral").strip().lower()
        info_edge = str((draft_window or {}).get("info_edge") or "even").strip().lower()
        team_side = str((draft_window or {}).get("team_side") or "blue").strip().lower()
        ally_slot_timing = str((draft_window or {}).get("ally_slot_timing") or "solo").strip().lower()
        ally_locked_count = int((draft_window or {}).get("ally_locked_count") or 0)
        enemy_locked_count = int((draft_window or {}).get("enemy_locked_count") or 0)
        if role_key == "jungle":
            total_locked = ally_locked_count + enemy_locked_count
            if total_locked <= 2:
                return "map-blind"
            if total_locked <= 5:
                return "map-semi"
            return "map-answered"
        if posture == "blind":
            return "blind-slot"
        if posture == "answer":
            return "answer-slot"
        if posture == "contest":
            return "contest-slot"
        if role_key in {"bottom", "support"}:
            if revealed_lane_roles == {"bottom"}:
                return "adc-revealed"
            if revealed_lane_roles == {"support"}:
                return "support-revealed"
            if lane_response_state == "answered":
                return "duo-answered"
        if lane_response_state == "semi":
            return "lane-semi"
        if lane_response_state == "answered":
            return "lane-answered"
        if lane_state == "partial":
            return "lane-partial"
        if lane_state == "full":
            return "lane-complete"
        if team_side == "blue" and ally_slot_timing == "early" and (current_pick or risk == "high"):
            return "blue-open"
        if team_side == "red" and ally_slot_timing == "late" and (current_pick or info_edge == "answering"):
            return "red-answer"
        if info_edge == "exposed" and (current_pick or risk == "high"):
            return "info-exposed"
        if info_edge == "answering" and current_pick:
            return "info-answering"
        if current_pick and risk == "high":
            return "protect-pick"
        if current_pick and risk in {"medium", "low"}:
            return "lane-protect"
        if risk == "high":
            return "draft-open"
        return "draft-shaped"

    def _classify_ban_focus(
        self,
        reasons: list[str] | tuple[str, ...],
        *,
        role: str | None = None,
        current_pick: ChampionKnowledge | None = None,
        stage: str = "ban",
    ) -> str:
        role_key = self._normalize_role(role or "")
        normalized_reasons = " | ".join(str(reason or "").strip().lower() for reason in reasons if reason).strip()
        if role_key == "jungle":
            if "pool" in normalized_reasons or "conforto" in normalized_reasons:
                return "anti-pool"
            if (
                "mapa" in normalized_reasons
                or "estrutura" in normalized_reasons
                or "engage" in normalized_reasons
                or "front line" in normalized_reasons
                or "burst" in normalized_reasons
                or "controle" in normalized_reasons
            ):
                return "anti-comp"
            return "anti-role"
        if current_pick and (
            "te pune direto" in normalized_reasons
            or "lane instavel" in normalized_reasons
            or "lane" in normalized_reasons
        ):
            return "anti-lane"
        if "pool" in normalized_reasons or "conforto" in normalized_reasons:
            return "anti-pool"
        if "front line" in normalized_reasons or "controle" in normalized_reasons or "engage" in normalized_reasons or "burst" in normalized_reasons:
            return "anti-comp"
        if str(stage or "").strip().lower() == "ban":
            return "anti-role"
        return "anti-comp"

    def _resolve_duo_bonus(self, champion_name: Any, role: str, allies: list[dict[str, Any]]) -> bool:
        if role not in {"bottom", "support"}:
            return False
        counterpart_role = "support" if role == "bottom" else "bottom"
        counterpart = next(
            (
                ally for ally in allies
                if self._normalize_role((ally or {}).get("role")) == counterpart_role
                and (ally or {}).get("champion")
            ),
            None,
        )
        if not counterpart:
            return False
        return bool(self.get_duo_synergy(champion_name, counterpart.get("champion")))

    def _resolve_jungle_bonus(self, champion_name: Any, role: str, allies: list[dict[str, Any]]) -> bool:
        jungle_ally = next(
            (
                ally for ally in allies
                if self._normalize_role((ally or {}).get("role")) == "jungle"
                and (ally or {}).get("champion")
            ),
            None,
        )
        if role == "jungle":
            lane_ally = next(
                (
                    ally for ally in allies
                    if self._normalize_role((ally or {}).get("role")) in {"mid", "top", "bottom", "support"}
                    and (ally or {}).get("champion")
                ),
                None,
            )
            if not lane_ally:
                return False
            return bool(self.get_jungle_lane_synergy(champion_name, lane_ally.get("champion")))
        if not jungle_ally:
            return False
        return bool(self.get_jungle_lane_synergy(jungle_ally.get("champion"), champion_name))


def _merge_unique(primary: list[str], secondary: list[str]) -> list[str]:
    seen = set()
    merged = []
    for item in [*(primary or []), *(secondary or [])]:
        if not item or item in seen:
            continue
        seen.add(item)
        merged.append(item)
    return merged


__all__ = ["BanRecommendation", "ChampionKnowledge", "ItemKnowledge", "LeagueKnowledgeBase"]
