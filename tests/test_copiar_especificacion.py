"""Spec copiar-especificacion — copiar la especificación al portapapeles."""
from __future__ import annotations

from PySide6.QtGui import QGuiApplication


def test_ce01_copia_completa(app):
    """CE-01: título + enunciado + columnas objetivo + orden."""
    app.cargar_preset("ejemplo_tienda.json")
    assert hasattr(app, "btn_copiar_spec")
    app.btn_copiar_spec.click()
    txt = QGuiApplication.clipboard().text()
    assert app.ejercicio.titulo in txt
    assert app.ejercicio.enunciado in txt
    assert "COLUMNAS OBJETIVO" in txt
    assert "ESPECIFICACIÓN COPIADA" in app.toast_msg


def test_ce02_sin_ejercicio(app):
    """CE-02: sin ejercicio → toast, portapapeles intacto."""
    from core.session_loader import Ejercicio
    app.ejercicio = Ejercicio()
    app._refresh_briefing()
    QGuiApplication.clipboard().setText("ANTES")
    app.btn_copiar_spec.click()
    assert "NADA QUE COPIAR" in app.toast_msg
    assert QGuiApplication.clipboard().text() == "ANTES"
