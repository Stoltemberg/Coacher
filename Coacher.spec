# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

project_dir = Path.cwd()
src_dir = project_dir / "src"
icon_path = src_dir / "assets" / "icon.ico"

datas = [
    (str(src_dir / "ui"), "ui"),
    (str(src_dir / "data"), "data"),
    (str(src_dir / "assets"), "assets"),
    (str(src_dir / ".env"), "."),
]

hiddenimports = [
    "edge_tts",
    "pygame",
    "webview.platforms.winforms",
    "webview.platforms.edgechromium",
]

a = Analysis(
    [str(src_dir / "app.py")],
    pathex=[str(src_dir)],
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
