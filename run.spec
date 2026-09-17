# -*- mode: python ; coding: utf-8 -*-
"""Spec de PyInstaller para SQLab (offline, onefile, windowed).

Uso (desde la raíz del repo):
    python -m PyInstaller run.spec

Genera dist/SQLab.exe incluyendo recursos (dark.qss, logo_sqllab.svg)
para conservar tema oscuro y logo en el binario portable.
"""
directories = {
    "resources": "resources",
    "examples": "examples",
}

a = Analysis(
    ["app.py"],
    pathex=["."],
    binaries=[],
    datas=[(src, dst) for src, dst in directories.items()],
    hiddenimports=["openpyxl", "xlrd"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="SQLab",
    icon="resources/logo_sqllab.ico",
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
)