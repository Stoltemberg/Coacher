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
                "first_reset_focus": role_profile.first_reset_focus if role_profile else "",
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
            "first_reset_focus": role_profile.first_reset_focus if role_profile else "",
        }

    def get_draft_guidance(self, my_champion: Any, enemy_team: list[Any], role: str | None = None) -> Optional[dict[str, Any]]:
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
            "first_reset_focus": role_profile.first_reset_focus if role_profile else "",
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

    def _build_focus(self, champion: ChampionKnowledge, threats: dict[str, int]) -> list[str]:
        focus = []
        if threats["hard_cc"] >= 2:
            focus.append("tenacidade ou defesa contra controle cedo")
        if threats["assassin"] >= 2:
            focus.append("seguro defensivo antes de build full ganancia")
        if threats["tank"] >= 2:
            focus.append("penetracao e dano consistente para luta longa")
        if threats["sustain"] >= 1:
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
        archetype = champion.archetype
        if archetype == "marksman":
            return ["anti-heal contra sustain", "penetracao contra front line pesada"]
        if archetype == "assassin":
            return ["ferramenta defensiva se o pickoff estiver arriscado", "penetração se armadura travar tua curva"]
        if archetype in {"control_mage", "burst_mage"}:
            return ["penetração mágica contra MR cedo", "seguro defensivo contra dive"]
        if archetype in {"engage_support", "tank"}:
            return ["tenacidade ou defesa reativa contra muito controle", "item utilitario para abrir luta ou proteger carry"]
        return ["adaptação situacional ao tab inimigo"]

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


def _merge_unique(primary: list[str], secondary: list[str]) -> list[str]:
    seen = set()
    merged = []
    for item in [*(primary or []), *(secondary or [])]:
        if not item or item in seen:
            continue
        seen.add(item)
        merged.append(item)
    return merged


__all__ = ["ChampionKnowledge", "ItemKnowledge", "LeagueKnowledgeBase"]
