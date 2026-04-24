"""Lightweight on-disk persistence for player memory."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

from core.app_paths import app_data_dir


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _default_base_dir() -> Path:
    override = os.getenv("COACHER_MEMORY_DIR")
    if override:
        return Path(override).expanduser()
    return app_data_dir()


def resolve_memory_store_path(custom_path: str | Path | None = None) -> Path:
    """Resolve the path used to store player memory on disk."""

    if custom_path is not None:
        return Path(custom_path).expanduser()

    override = os.getenv("COACHER_MEMORY_PATH")
    if override:
        return Path(override).expanduser()

    return _default_base_dir() / "player_memory.json"


@dataclass(slots=True)
class MemoryStore:
    """Small JSON store with atomic writes."""

    path: Path

    def __post_init__(self) -> None:
        self.path = Path(self.path).expanduser()

    @classmethod
    def default(cls, custom_path: str | Path | None = None) -> "MemoryStore":
        return cls(resolve_memory_store_path(custom_path))

    def exists(self) -> bool:
        return self.path.exists()

    def _quarantine_invalid_store(self) -> None:
        timestamp = _utc_now().strftime("%Y%m%d-%H%M%S")
        quarantine_path = self.path.with_name(f"{self.path.stem}.corrupt-{timestamp}{self.path.suffix}")

        try:
            if self.path.exists():
                self.path.replace(quarantine_path)
        except OSError:
            # If we cannot move the broken file, loading should still fail safe.
            pass

    def load(self) -> dict[str, Any] | None:
        if not self.path.exists():
            return None

        try:
            raw_text = self.path.read_text(encoding="utf-8").strip()
        except OSError:
            return None

        if not raw_text:
            return None

        try:
            payload = json.loads(raw_text)
        except json.JSONDecodeError:
            self._quarantine_invalid_store()
            return None

        if not isinstance(payload, dict):
            self._quarantine_invalid_store()
            return None

        if "memory" in payload:
            memory_payload = payload.get("memory")
            if isinstance(memory_payload, dict):
                return memory_payload
            if memory_payload is not None:
                self._quarantine_invalid_store()
                return None

        return payload

    def save(self, payload: dict[str, Any]) -> bool:
        self.path.parent.mkdir(parents=True, exist_ok=True)

        wrapper = {
            "version": 1,
            "saved_at": _utc_now().isoformat(),
            "memory": payload,
        }
        serialized = json.dumps(wrapper, ensure_ascii=False, indent=2, sort_keys=True)

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
                os.fsync(handle.fileno())
            tmp_file.replace(self.path)
            return True
        except Exception:
            if tmp_file is not None and tmp_file.exists():
                try:
                    tmp_file.unlink()
                except OSError:
                    pass
            return False

    def delete(self) -> bool:
        try:
            if self.path.exists():
                self.path.unlink()
            return True
        except OSError:
            return False


__all__ = [
    "MemoryStore",
    "resolve_memory_store_path",
]
