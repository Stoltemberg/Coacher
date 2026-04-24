# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path


project_dir = Path(globals().get("SPEC", "Coacher.spec")).resolve().parent
app_dir = project_dir
icon_path = app_dir / "assets" / "icon.ico"


def collect_tree(root: Path, bundle_root: str, *, excluded_suffixes: set[str] | None = None):
    if not root.exists():
        return []

    entries = []
    excluded_suffixes = {suffix.lower() for suffix in (excluded_suffixes or set())}

    for file_path in root.rglob("*"):
        if not file_path.is_file():
            continue
        if file_path.suffix.lower() in excluded_suffixes:
            continue

        relative_parent = file_path.relative_to(root).parent
        target_dir = Path(bundle_root)
        if str(relative_parent) != ".":
            target_dir = target_dir / relative_parent

        entries.append((str(file_path), str(target_dir)))

    return entries


datas = []
datas += collect_tree(
    app_dir / "ui",
    "ui",
    excluded_suffixes={".exe", ".ps1", ".map", ".txt"},
)
datas += collect_tree(app_dir / "assets", "assets")
datas += collect_tree(app_dir / "data" / "league_knowledge", "data/league_knowledge")

hiddenimports = [
    "edge_tts",
    "pygame",
    "webview.platforms.winforms",
    "webview.platforms.edgechromium",
    "http.server",
    "socketserver",
]

a = Analysis(
    [str(app_dir / "app.py")],
    pathex=[str(app_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="Coacher",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(icon_path) if icon_path.exists() else None,
)
