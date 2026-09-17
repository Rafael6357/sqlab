"""Unit — Icono del ejecutable (spec: icono-ejecutable).

Valida que el .ico del logo exista, sea un ICO válido multi-imagen y que
run.spec lo referencie en el bloque EXE().
"""
from __future__ import annotations

import os
import struct

REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
ICO_PATH = os.path.join(REPO_ROOT, "resources", "logo_sqllab.ico")
SPEC_PATH = os.path.join(REPO_ROOT, "run.spec")


def test_ico_existe():
    """IC-01: el archivo logo_sqllab.ico está versionado en resources/."""
    assert os.path.isfile(ICO_PATH), f"No existe {ICO_PATH} (ejecutar bin/make_icon.py)"


def test_ico_multi_imagen():
    """IC-01: ICO válido con las 7 entradas esperadas (16–256)."""
    with open(ICO_PATH, "rb") as f:
        data = f.read()
    assert len(data) > 1000, "ICO sospechosamente pequeño"
    reserved, tipo, count = struct.unpack("<HHH", data[:6])
    assert (reserved, tipo) == (0, 1), "Magic ICO inválido"
    assert count == 7, f"Se esperaban 7 imágenes, hay {count}"
    tamanos = set()
    for i in range(count):
        entry = data[6 + i * 16: 6 + (i + 1) * 16]
        w, h = entry[0], entry[1]
        tamanos.add(w if w else 256)
    assert tamanos == {16, 24, 32, 48, 64, 128, 256}, f"Tamaños inesperados: {tamanos}"


def test_run_spec_referencia_icono():
    """IC-02: run.spec contiene icon= apuntando al .ico existente."""
    with open(SPEC_PATH, "r", encoding="utf-8") as f:
        texto = f.read()
    assert "logo_sqllab.ico" in texto, "run.spec no referencia logo_sqllab.ico"
    assert "icon=" in texto, "run.spec no define icon= en EXE()"
    assert os.path.isfile(ICO_PATH)
