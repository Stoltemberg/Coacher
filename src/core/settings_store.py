"""Persistent user settings storage."""

from __future__ import annotations

import json
import threading
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any


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
            return settings if isinstance(settings, dict) else {}

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

