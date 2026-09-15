"""Genera app-sql-offline/resources/logo_sqllab.ico desde logo_sqllab.svg.

Renderiza el SVG con QSvgRenderer a 256 px, reescala a 16/24/32/48/64/128/256
y ensambla un ICO multi-entrada con PNG embebidos (válido desde Windows Vista).

Uso (desde la raíz del repo):
    python bin/make_icon.py

Solo requiere PySide6 (QtSvg) + stdlib. Salida determinista (idempotente).
"""
from __future__ import annotations

import os
import struct
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QBuffer, QIODevice, Qt
from PySide6.QtGui import QImage, QPainter
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QApplication

TAMANOS = (16, 24, 32, 48, 64, 128, 256)


def _render_png(svg_path: str, size: int) -> bytes:
    """Renderiza el SVG a PNG (bytes) del tamaño indicado."""
    fuente = QImage(256, 256, QImage.Format.Format_ARGB32)
    fuente.fill(0)
    painter = QPainter(fuente)
    QSvgRenderer(svg_path).render(painter)
    painter.end()
    img = fuente if size == 256 else fuente.scaled(
        size, size,
        aspectMode=Qt.AspectRatioMode.IgnoreAspectRatio,
        mode=Qt.TransformationMode.SmoothTransformation,
    )
    buf = QBuffer()
    buf.open(QIODevice.OpenModeFlag.WriteOnly)
    if not img.save(buf, "PNG"):
        raise RuntimeError(f"No se pudo codificar PNG de {size}px")
    return bytes(buf.data())


def _ensamblar_ico(imagenes: list[tuple[int, bytes]]) -> bytes:
    """Ensambla un ICO (ICONDIR + entradas + PNG) con las (tamaño, bytes)."""
    cabecera = struct.pack("<HHH", 0, 1, len(imagenes))
    offset = 6 + 16 * len(imagenes)
    directorio = b""
    cuerpos = b""
    for size, png in imagenes:
        lado = 0 if size >= 256 else size
        directorio += struct.pack(
            "<BBBBHHII", lado, lado, 0, 0, 1, 32, len(png), offset
        )
        offset += len(png)
        cuerpos += png
    return cabecera + directorio + cuerpos


def main() -> int:
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    svg = os.path.join(raiz, "app-sql-offline", "resources", "logo_sqllab.svg")
    ico = os.path.join(raiz, "app-sql-offline", "resources", "logo_sqllab.ico")
    if not os.path.isfile(svg):
        print(f"ERROR: no existe {svg}", file=sys.stderr)
        return 1
    _qt = QApplication.instance() or QApplication([])
    imagenes = [(s, _render_png(svg, s)) for s in TAMANOS]
    with open(ico, "wb") as f:
        f.write(_ensamblar_ico(imagenes))
    print(f"OK: {ico} ({len(imagenes)} tamanos, {os.path.getsize(ico)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
