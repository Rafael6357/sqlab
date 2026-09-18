"""Spec mostrar-null-en-grillas — None se ve como NULL tenue, no vacío."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication

from ui.tablas import _ajustar_anchos, _item_grilla

TENUE = QColor("#4d7c6d")


def test_nl01_item_none_muestra_null_tenue():
    """NL-01/02 unit: None → texto NULL, tooltip NULL, tenue + cursiva, sin align derecha."""
    item = _item_grilla(None)
    assert item.text() == "NULL"
    assert item.toolTip() == "NULL"
    assert item.foreground().color() == TENUE
    assert item.font().italic()
    assert item.textAlignment() != Qt.AlignmentFlag.AlignRight


def test_nl03_cadena_vacia_sigue_vacia():
    """NL-03: '' → celda vacía sin tooltip (distinguible de NULL)."""
    item = _item_grilla("")
    assert item.text() == ""
    assert item.toolTip() == ""


def test_nl04_escalares_intactos():
    """NL-04: 0/0.0/False/strings tal cual; int/float a la derecha."""
    assert _item_grilla(0).text() == "0"
    assert _item_grilla(0.0).text() == "0.0"
    assert _item_grilla(False).text() == "False"
    assert _item_grilla("hola").text() == "hola"
    assert _item_grilla(7).textAlignment() == Qt.AlignmentFlag.AlignRight
    assert _item_grilla(2.5).textAlignment() == Qt.AlignmentFlag.AlignRight
    assert _item_grilla("x").textAlignment() != Qt.AlignmentFlag.AlignRight


def test_nl01_visor_pinta_null(app, qtbot):
    """NL-01 E2E: visor muestra NULL en celdas None."""
    from core.sqlite_engine import Column, Table
    t = Table(
        name="t",
        columns=[Column(name="a", type="TEXT"), Column(name="b", type="TEXT")],
        rows=[[None, "x"], ["y", None]],
    )
    app._refresh_dump(t)
    qtbot.wait(50)
    QApplication.processEvents()
    assert app.visor_tabla.item(0, 0).text() == "NULL"
    assert app.visor_tabla.item(0, 1).text() == "x"
    assert app.visor_tabla.item(1, 1).text() == "NULL"


def test_nl02_resultado_pinta_null(app, qtbot):
    """NL-02 E2E: resultado muestra NULL en celdas None."""
    app._mostrar_resultado(["a", "b"], [[None, "x"], ["y", None]])
    qtbot.wait(50)
    QApplication.processEvents()
    assert app.resultado_tabla.item(0, 0).text() == "NULL"
    assert app.resultado_tabla.item(1, 1).text() == "NULL"
    assert app.resultado_tabla.item(0, 1).text() == "x"


def test_nl05_anchos_miden_null(app, qtbot):
    """NL-05: la columna con None no queda más estrecha que el literal NULL."""
    from PySide6.QtWidgets import QTableWidget
    grilla = QTableWidget()
    grilla.setColumnCount(1)
    _ajustar_anchos(grilla, ["a"], [[None]], 100)
    qtbot.wait(20)
    QApplication.processEvents()
    esperado = grilla.fontMetrics().horizontalAdvance("NULL") + 20
    assert grilla.columnWidth(0) >= min(esperado, 300)
