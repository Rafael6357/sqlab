"""Spec exportar-db — volcar la memoria a .db real (ED)."""
from __future__ import annotations


def _eng_con_datos():
    from core.sqlite_engine import Column, SQLEngine, Table
    e = SQLEngine()
    e.load_tables([
        Table(name="t", columns=[Column("id", "INTEGER"), Column("n", "TEXT")],
              rows=[[1, "Ana"], [2, None]]),
    ])
    return e


def test_ed01_roundtrip(tmp_path):
    """ED-01: exportar → reabrir → mismos datos y nulos."""
    from core.session_loader import load_file
    p = tmp_path / "base.db"
    _eng_con_datos().exportar_db(str(p))
    res = load_file(str(p))
    assert res.ok, res.errors
    assert [t.name for t in res.tables] == ["t"]
    assert res.tables[0].rows == [[1, "Ana"], [2, None]]


def test_ed03_sin_datos_error():
    """ED-03: motor vacío → ValueError, sin fichero."""
    import pytest
    from core.sqlite_engine import SQLEngine
    with pytest.raises(ValueError):
        SQLEngine().exportar_db("x.db")


def test_ed02_boton_y_vacio(app, monkeypatch, tmp_path):
    """ED-02/ED-03: botón existe; sin tablas → toast sin diálogo."""
    from PySide6.QtWidgets import QFileDialog
    assert hasattr(app, "btn_exportar_db")
    assert app.btn_exportar_db.text() == "EXPORTAR DB"
    llamadas = []
    monkeypatch.setattr(
        QFileDialog, "getSaveFileName",
        lambda *a, **k: (llamadas.append(1), ("x",))[1],
    )
    app.engine.close()
    app.engine.tables = {}
    app.exportar_db()
    assert llamadas == []
    assert "NADA QUE EXPORTAR" in app.toast_msg


def test_ed02_exporta_desde_ui(app, monkeypatch, tmp_path):
    """ED-02: desde la UI con datos → fichero válido en el formato del motor."""
    from PySide6.QtWidgets import QFileDialog
    app.cargar_preset("ejemplo_tienda.json")
    dest = tmp_path / ("ui.sql" if app.engine.dialect == "POSTGRESQL" else "ui.db")
    monkeypatch.setattr(
        QFileDialog, "getSaveFileName",
        lambda *a, **k: (str(dest), "x"),
    )
    app.exportar_db()
    assert dest.exists()
    if app.engine.dialect == "POSTGRESQL":
        assert "clientes" in dest.read_text(encoding="utf-8", errors="replace")
    else:
        from core.session_loader import load_file
        res = load_file(str(dest))
        assert res.ok, res.errors
        assert {t.name for t in res.tables} >= {"clientes", "pedidos"}
