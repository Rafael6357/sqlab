"""Spec fix-matriz-resultados — splitter matriz/editor nunca colapsa a 0."""
from __future__ import annotations

import pytest


def test_matriz_splitter_no_colapsable(app):
    """MR-01: el splitter matriz/editor no es colapsable en ningún lado."""
    assert hasattr(app, "work_splitter"), "MainWindow debe exponer work_splitter"
    assert not app.work_splitter.isCollapsible(0), "panel 0 (editor) no debe ser colapsable"
    assert not app.work_splitter.isCollapsible(1), "panel 1 (matriz) no debe ser colapsable"


def test_matriz_minimum_widths(app):
    """MR-01: paneles mantienen mínimos para que el handle siempre sea alcanzable."""
    assert hasattr(app, "editor_pane"), "MainWindow debe exponer editor_pane"
    assert hasattr(app, "output_pane"), "MainWindow debe exponer output_pane"
    assert app.editor_pane.minimumWidth() >= 220, f"editor minimumWidth={app.editor_pane.minimumWidth()} < 220"
    assert app.output_pane.minimumWidth() >= 240, f"output minimumWidth={app.output_pane.minimumWidth()} < 240"


def test_matriz_handle_width(app):
    """MR-01: handle con área de agarre usable (>=4px)."""
    assert app.work_splitter.handleWidth() >= 4, f"handleWidth={app.work_splitter.handleWidth()} < 4"


def test_matriz_handle_recuperable(app, qtbot):
    """MR-01: arrastrar al extremo no deja a 0; clamp por minimumWidth."""
    app.show()
    qtbot.waitExposed(app)
    app.work_splitter.setSizes([0, 1000])
    qtbot.wait(30)
    # Procesar eventos para que el splitter aplique clamp
    from PySide6.QtWidgets import QApplication
    QApplication.processEvents()
    w0 = app.work_splitter.widget(0).width()
    w1 = app.work_splitter.widget(1).width()
    assert w0 >= 220, f"editor no recuperable: width={w0}"
    assert w1 >= 240, f"matriz no recuperable: width={w1}"


def test_matriz_doble_click_reset(app, qtbot):
    """MR-02: doble-clic en el handle resetea a ~50/50."""
    app.show()
    qtbot.waitExposed(app)
    assert hasattr(app, "_reset_work_splitter"), "MainWindow debe tener _reset_work_splitter para MR-02"
    app.work_splitter.setSizes([700, 100])
    qtbot.wait(20)
    app._reset_work_splitter()
    qtbot.wait(20)
    s0, s1 = app.work_splitter.sizes()
    # Tras reset ambos deben ser >200 y cercanos entre sí (tolerancia 50px por mínimos/bordes)
    assert s0 > 200 and s1 > 200, f"reset falló: sizes={[s0, s1]}"
    assert abs(s0 - s1) <= 60, f"reset no es ~50/50: sizes={[s0, s1]}"


def test_matriz_qss_handle_visual(app=None):
    """Unit: el handle visual sigue fino (1px) con margen para hit-area."""
    import os
    import re
    qss_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "resources", "dark.qss"))
    with open(qss_path, "r", encoding="utf-8") as f:
        qss = f.read()
    # Busca la regla del handle horizontal
    m = re.search(r"QSplitter::handle:horizontal\s*\{([^}]*)\}", qss, re.DOTALL)
    assert m, "No existe la regla QSplitter::handle:horizontal en dark.qss"
    bloque = m.group(1)
    assert "1px" in bloque, "El handle horizontal debe declarar 1px visual"
