"""Spec scrollbars-visibles — scrollbars brillantes siempre visibles (QSS)."""
from __future__ import annotations

import os
import re


def _qss() -> str:
    qss_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "resources", "dark.qss"))
    with open(qss_path, "r", encoding="utf-8") as f:
        return f.read()


def _bloque(qss: str, selector: str) -> str:
    m = re.search(rf"{re.escape(selector)}\s*\{{([^}}]*)\}}", qss, re.DOTALL)
    assert m, f"No existe la regla {selector} en dark.qss"
    return m.group(1)


def test_sb01_handle_siempre_visible():
    """SB-01: handle base en verde dim #00aa70 (no el gris #173834)."""
    qss = _qss()
    for sel in ("QScrollBar::handle:vertical", "QScrollBar::handle:horizontal"):
        bloque = _bloque(qss, sel)
        assert "#00aa70" in bloque, f"{sel} sin verde dim visible"
        assert "#173834" not in bloque, f"{sel} aún usa el gris apagado"


def test_sb02_hover_fosforo():
    """SB-02: hover del handle en fósforo #00ffaa."""
    qss = _qss()
    assert "QScrollBar::handle:vertical:hover" in qss
    assert "QScrollBar::handle:horizontal:hover" in qss
    for sel in ("QScrollBar::handle:vertical:hover", "QScrollBar::handle:horizontal:hover"):
        assert "#00ffaa" in _bloque(qss, sel), f"{sel} sin brillo fósforo"


def test_sb03_grosor_usable():
    """SB-03: ancho/alto >= 10px y handle mínimo >= 24px."""
    qss = _qss()
    mv = re.search(r"QScrollBar:vertical\s*\{([^}]*)\}", qss, re.DOTALL).group(1)
    mh = re.search(r"QScrollBar:horizontal\s*\{([^}]*)\}", qss, re.DOTALL).group(1)
    w = int(re.search(r"width:\s*(\d+)px", mv).group(1))
    h = int(re.search(r"height:\s*(\d+)px", mh).group(1))
    assert w >= 10, f"scrollbar vertical de {w}px"
    assert h >= 10, f"scrollbar horizontal de {h}px"
    assert "min-height: 24px" in _bloque(qss, "QScrollBar::handle:vertical")
    assert "min-width: 24px" in _bloque(qss, "QScrollBar::handle:horizontal")


def test_sb04_sin_flechas_ni_claro():
    """SB-04: sin flechas; en reglas scrollbar solo paleta oscura + verdes."""
    qss = _qss()
    assert "add-line:vertical" in qss and "height: 0" in qss
    assert "add-line:horizontal" in qss and "width: 0" in qss
    bloques = "".join(
        m.group(1)
        for m in re.finditer(r"QScrollBar[^{]*\{([^}]*)\}", qss, re.DOTALL)
    ).lower()
    for claro in ("#ffffff", "#eeeeee", "#dddddd", "#cccccc"):
        assert claro not in bloques, f"variante clara {claro} en scrollbar"
    for permitido in ("#060b0b", "#00aa70", "#00ffaa"):
        assert permitido in bloques, f"falta color de paleta {permitido} en scrollbar"
