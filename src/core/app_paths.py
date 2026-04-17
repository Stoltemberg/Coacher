"""Shared runtime paths for packaged and development builds."""

from __future__ import annotations

import os
import sys
from pathlib import Path


APP_NAME = "Coacher"


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def bundled_root() -> Path:
    if getattr(sys, "_MEIPASS", None):
        return Path(sys._MEIPASS)
    return project_root()


def executable_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return project_root()


def app_data_dir() -> Path:
    override = os.getenv("COACHER_DATA_DIR")
    if override:
        return Path(override).expanduser()

    appdata = os.getenv("LOCALAPPDATA") or os.getenv("APPDATA")
    if appdata:
        return Path(appdata).expanduser() / APP_NAME

    return Path.home() / f".{APP_NAME.lower()}"


def resource_path(*parts: str) -> Path:
    return bundled_root().joinpath(*parts)


def writable_data_path(*parts: str) -> Path:
    path = app_data_dir().joinpath(*parts)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path

