"""Persistent user settings storage."""

from __future__ import annotations

import json
import threading
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

from core.voice_catalog import normalize_voice_personality, normalize_voice_preset


def _normalize_preferred_pool(value: Any) -> list[str]:
    if isinstance(value, str):
        raw_items = value.replace("\r", "\n").replace(";", "\n").replace(",", "\n").split("\n")
    elif isinstance(value, (list, tuple, set)):
        raw_items = list(value)
    else:
        raw_items = []

    normalized: list[str] = []
    seen: set[str] = set()
    for item in raw_items:
        text = str(item or "").strip()
        if not text:
            continue
        key = text.casefold()
        if key in seen:
            continue
        seen.add(key)
        normalized.append(text)

    return normalized[:20]


DEFAULT_SETTINGS = {
    "volume": 50,
    "voice_enabled": True,
    "objectives_enabled": True,
    "hardcore_enabled": False,
    "voice_preset": "standard",
    "voice_personality": "standard",
    "solo_focus": True,
    "macro_interval": 30,
    "minimap_interval": 10,
    "economy_interval": 60,
    "item_check_interval": 120,
    "farm_threshold": 8.0,
    "vision_threshold": 1.2,
    "preferred_champion_pool": [],
    "prioritize_pool_picks": True,
    "category_filters": {
        "draft": True,
        "lane": True,
        "macro": True,
        "objective": True,
        "economy": True,
        "recovery": True
    }
}


class SettingsStore:
    def __init__(self, path: str | Path):
        self.path = Path(path).expanduser()
        self._lock = threading.Lock()

    def _read_all(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"version": 1, "accounts": {}}

        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {"version": 1, "accounts": {}}

        if not isinstance(payload, dict):
            return {"version": 1, "accounts": {}}

        accounts = payload.get("accounts")
        if not isinstance(accounts, dict):
            accounts = {}

        return {
            "version": payload.get("version", 1),
            "accounts": accounts,
        }

    def load(self, account_key: str) -> dict[str, Any]:
        key = str(account_key or "").strip() or "__default__"
        with self._lock:
            payload = self._read_all()
            settings = payload["accounts"].get(key, {})
            if not isinstance(settings, dict):
                settings = {}
            
            # Merge defaults
            merged = DEFAULT_SETTINGS.copy()
            merged.update(settings)
            
            # Deep merge for dictionary keys like category_filters
            if "category_filters" in settings and isinstance(settings["category_filters"], dict):
                merged_filters = DEFAULT_SETTINGS["category_filters"].copy()
                merged_filters.update(settings["category_filters"])
                merged["category_filters"] = merged_filters

            merged["voice_personality"] = normalize_voice_personality(
                merged.get("voice_personality", DEFAULT_SETTINGS["voice_personality"])
            )
            merged["voice_preset"] = normalize_voice_preset(
                merged.get("voice_preset", DEFAULT_SETTINGS["voice_preset"])
            )
            merged["preferred_champion_pool"] = _normalize_preferred_pool(
                merged.get("preferred_champion_pool", DEFAULT_SETTINGS["preferred_champion_pool"])
            )
            merged["prioritize_pool_picks"] = bool(
                merged.get("prioritize_pool_picks", DEFAULT_SETTINGS["prioritize_pool_picks"])
            )
                
            return merged

    def save(self, account_key: str, settings: dict[str, Any]) -> bool:
        key = str(account_key or "").strip() or "__default__"
        with self._lock:
            payload = self._read_all()
            payload["accounts"][key] = settings
            return self._write_all(payload)

    def _write_all(self, payload: dict[str, Any]) -> bool:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        serialized = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)

        tmp_file = None
        try:
            with NamedTemporaryFile(
                "w",
                encoding="utf-8",
                delete=False,
                dir=str(self.path.parent),
                prefix=f".{self.path.stem}.",
                suffix=".tmp",
            ) as handle:
                tmp_file = Path(handle.name)
                handle.write(serialized)
                handle.flush()
            tmp_file.replace(self.path)
            return True
        except Exception:
            if tmp_file and tmp_file.exists():
                try:
                    tmp_file.unlink()
                except OSError:
                    pass
            return False

    def get_all(self, account_key: str = None) -> dict[str, Any]:
        """Returns all settings for a given account (defaults to __default__)."""
        return self.load(account_key)

    def get(self, key: str, default: Any = None, account_key: str = None) -> Any:
        """Returns a specific setting value."""
        return self.load(account_key).get(key, default)

    def update(self, key: str, value: Any, account_key: str = None) -> bool:
        """Updates a specific setting value and persists to disk."""
        settings = self.load(account_key)
        settings[key] = value
        return self.save(account_key, settings)
