"""Spec consola-vacia-inicial — la consola abre vacía (CV-01)."""
from __future__ import annotations


def test_cv01_editor_vacio_al_arrancar(app):
    """CV-01: editor sin texto al arrancar, pero con tablas Tienda cargadas."""
    assert app.editor.toPlainText() == ""
    assert set(app.engine.table_names()) >= {"clientes", "pedidos"}
