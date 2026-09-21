"""Spec auto-espaciado-columnas — ajuste a contenido + reparto proporcional."""
from __future__ import annotations

from PySide6.QtWidgets import QApplication


def test_ae01_cabecera_completa_visible(app, qtbot):
    """AE-01: nombre de columna largo no recortado por estrechez inicial."""
    cols = ["id", "CuantosAñosMedicamento1"]
    app._mostrar_resultado(cols, [[1, 2]])
    qtbot.wait(50)
    QApplication.processEvents()
    header = app.resultado_tabla.horizontalHeader()
    fm = app.resultado_tabla.fontMetrics()
    esperado = fm.horizontalAdvance("CuantosAñosMedicamento1") + 20
    assert header.sectionSize(1) >= min(esperado, 300)


def test_ae02_reparto_proporcional_al_estirar(app, qtbot):
    """AE-02: al ensanchar, el extra se reparte en proporción a la base."""
    from ui.tablas import repartir_anchos_proporcional
    cols = ["a", "bbbbb"]
    app._mostrar_resultado(cols, [["x", "y"]])
    qtbot.wait(50)
    QApplication.processEvents()
    grilla = app.resultado_tabla
    base = [grilla.horizontalHeader().sectionSize(i) for i in range(2)]
    grilla.setProperty("anchos_base", base)
    ancho_antes = sum(base)
    # Simular panel más ancho: forzar viewport grande vía mínimo y repartir
    grilla.setMinimumWidth(ancho_antes + 400)
    qtbot.wait(100)
    QApplication.processEvents()
    repartir_anchos_proporcional(grilla)
    despues = [grilla.horizontalHeader().sectionSize(i) for i in range(2)]
    assert sum(despues) > ancho_antes
    # proporción conservada (tolerancia por redondeo)
    assert abs(despues[1] / despues[0] - base[1] / base[0]) < 0.15


def test_ae03_angosta_sin_hueco(app, qtbot):
    """AE-03: tabla angosta llena el viewport (sin stretch global)."""
    assert not app.resultado_tabla.horizontalHeader().stretchLastSection()
    app._mostrar_resultado(["a", "b"], [["1", "2"]])
    qtbot.wait(50)
    QApplication.processEvents()
    grilla = app.resultado_tabla
    total = sum(grilla.horizontalHeader().sectionSize(i) for i in range(2))
    assert total >= grilla.viewport().width() - 40
