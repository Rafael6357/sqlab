# -*- mode: python ; coding: utf-8 -*-
"""Spec de PyInstaller para SQLab (offline, onefile, windowed).

Uso (desde la raíz del repo):
    python -m PyInstaller run.spec

Genera dist/SQLab.exe incluyendo recursos (dark.qss, logo_sqllab.svg)
y binarios PostgreSQL vendoreados (pgsql/) para el motor embebido.
"""
import os

directories = {
    "resources": "resources",
    "examples": "examples",
}

# Binarios PG 17.11 vendoreados (F6 migración PG; ver specs/postgres-embebido-spike.md).
# Solo existen en máquinas con D:\pg-bin\vendor; si faltan, el build sigue
# y la app muestra "MOTOR NO DISPONIBLE" al arrancar.
_pgsql = r"D:\pg-bin\vendor\pgsql"
_datas = [(src, dst) for src, dst in directories.items()]
if os.path.isdir(_pgsql):
    _datas.append((_pgsql, "pgsql"))

a = Analysis(
    ["app.py"],
    pathex=["."],
    binaries=[],
    datas=_datas,
    hiddenimports=["openpyxl", "xlrd", "PySide6.QtCharts"],
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