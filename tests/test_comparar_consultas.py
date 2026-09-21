"""Spec comparar-consultas — comparar 2 consultas del historial (CP)."""
from __future__ import annotations


def _eng():
    from core.session_loader import load_file
    from core.sqlite_engine import SQLEngine
    import os
    base = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "examples", "ejemplo_tienda.json"))
    res = load_file(base)
    assert res.ok, res.errors
    e = SQLEngine()
    e.load_tables(res.tables)
    return e


def test_cp01_iguales():
    """CP-01: misma consulta dos veces → iguales con conteo."""
    from core.comparar import comparar_consultas
    v = comparar_consultas("SELECT * FROM clientes", "SELECT * FROM clientes", _eng())
    assert v["iguales"] and not v["solo_orden"]
    assert "FILAS" in v["resumen"]


def test_cp02_distintas():
    """CP-02: filas y columnas distintas → veredicto + diff topado."""
    from core.comparar import comparar_consultas
    e = _eng()
    v = comparar_consultas("SELECT * FROM clientes", "SELECT * FROM clientes WHERE id = 1", e)
    assert not v["iguales"] and not v["solo_orden"]
    assert "vs" in v["resumen"] and v["diff"]
    v = comparar_consultas("SELECT id FROM clientes", "SELECT nombre FROM clientes", e)
    assert not v["iguales"] and "COLUMNAS" in v["resumen"]


def test_cp02_solo_orden():
    """CP edge: mismo multiset, distinto orden → aviso de ORDER BY."""
    from core.comparar import comparar_consultas
    e = _eng()
    v = comparar_consultas(
        "SELECT id FROM clientes ORDER BY id DESC",
        "SELECT id FROM clientes ORDER BY id ASC",
        e,
    )
    assert not v["iguales"] and v["solo_orden"] and "ORDER BY" in v["resumen"]


def test_cp04_error():
    """CP-04: consulta que falla → error reportado sin crash."""
    from core.comparar import comparar_consultas
    v = comparar_consultas("SELECT * FROM nada", "SELECT 1", _eng())
    assert not v["iguales"] and v["resumen"].startswith("ERROR EN A")


def test_cp03_dialogo_y_boton(app, qtbot, monkeypatch):
    """CP-03: botón COMPARAR; con <2 entradas → toast."""
    from PySide6.QtWidgets import QApplication
    assert hasattr(app, "btn_comparar")
    app.historial_list.clear()
    app.btn_comparar.click()
    qtbot.wait(30)
    QApplication.processEvents()
    assert "2 CONSULTAS" in app.toast_msg
