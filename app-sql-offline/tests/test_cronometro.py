"""E2E — Cronómetro / temporizador por ejercicio (spec: cronometro-ejercicio).

Verifica el marco CronoFrame del HUD: modo CRONO (cuenta arriba), modo TEMPO
(cuenta regresiva), reinicio manual y reset automático al cargar ejercicio.
Usa el fixture `app` (MainWindow) de conftest.py.
"""
from __future__ import annotations

import os

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QPushButton, QSpinBox, QToolButton

from ui.main_window import MainWindow

EXAMPLES = os.path.join(os.path.dirname(__file__), "..", "examples")


def _load_preset(w: MainWindow, filename: str = "ejemplo_tienda.json") -> None:
    """Carga un preset directamente sin diálogo de archivos."""
    path = os.path.normpath(os.path.join(EXAMPLES, filename))
    from core.session_loader import load_file
    result = load_file(path)
    w._aplicar_resultado(result, path)


# ── CR-01: control visible en el HUD ─────────────────────────────────────

def test_crono_frame_visible_en_hud(app):
    """CR-01: CronoFrame existe con todos sus controles."""
    frame = app.findChild(QFrame, "CronoFrame")
    assert frame is not None and frame.isVisible()
    assert app.findChild(type(app.crono_time), "CronoTime") is not None
    assert isinstance(app.crono_mode, QToolButton)
    assert isinstance(app.crono_start, QPushButton)
    assert isinstance(app.crono_reset, QPushButton)
    assert isinstance(app.crono_spin, QSpinBox)


def test_crono_estado_inicial(app):
    """CR-01: estado inicial 00:00:00, detenido, modo CRONO."""
    assert app.crono_time.text() == "00:00:00"
    assert not app.crono_mode.isChecked()
    assert app.crono_mode.text() == "CRONO"
    assert app.crono_start.text() == "INICIAR"
    assert not app.crono_spin.isVisible()  # spin solo en modo TEMPO
    assert not app.crono_activo


def test_crono_spin_rango(app):
    """CR-03: el spin del temporizador se limita a 5–3600 s."""
    assert app.crono_spin.minimum() == 5
    assert app.crono_spin.maximum() == 3600


# ── CR-02: cronómetro cuenta hacia arriba ────────────────────────────────

def test_cronometro_avanza(app, qtbot):
    """CR-02: INICIAR hace avanzar CronoTime; PAUSAR lo congela."""
    app.crono_mode.setChecked(False)
    app.crono_start.click()
    assert app.crono_start.text() == "PAUSAR"
    assert app.crono_activo
    qtbot.waitUntil(lambda: app.crono_time.text() != "00:00:00", timeout=5000)
    primero = app.crono_time.text()
    app.crono_start.click()  # pausar
    assert not app.crono_activo
    assert app.crono_start.text() == "INICIAR"
    congelado = app.crono_time.text()
    qtbot.wait(1100)
    assert app.crono_time.text() == congelado, "El cronómetro avanzó estando pausado"


# ── CR-03: temporizador cuenta regresiva ─────────────────────────────────

def test_temporizador_desciende(app, qtbot):
    """CR-03: en modo TEMPO el display desciende desde N."""
    app.crono_mode.setChecked(True)
    app._on_crono_mode(True)
    app.crono_spin.setValue(5)
    app.crono_start.click()
    assert app.crono_activo
    inicial = app.crono_time.text()
    assert inicial == "00:00:05"
    qtbot.waitUntil(lambda: app.crono_time.text() != inicial, timeout=5000)
    assert app.crono_time.text() < inicial


def test_temporizador_tiempo_agotado(app, qtbot):
    """CR-03: al llegar a cero se detiene, alerta roja y toast."""
    app.crono_mode.setChecked(True)
    app._on_crono_mode(True)
    app.crono_spin.setValue(5)
    # Simular que solo queda ~0 s por delante para no esperar 5 s reales
    import time as _time
    app.crono_start.click()
    app._crono_base = _time.monotonic() - 5.0
    app._crono_tick()
    assert not app.crono_activo, "El temporizador no se detuvo al llegar a cero"
    assert app.crono_time.text() == "00:00:00"
    assert app.crono_alerta, "No se activó el estado de alerta"
    assert app.exec_time.text() == "TIEMPO AGOTADO"


def test_editar_spin_en_marcha_reinicia(app, qtbot):
    """Edge: editar segundos en marcha detiene y reinicia."""
    app.crono_mode.setChecked(True)
    app._on_crono_mode(True)
    app.crono_spin.setValue(60)
    app.crono_start.click()
    assert app.crono_activo
    app.crono_spin.setValue(120)
    assert not app.crono_activo
    assert app.crono_time.text() == "00:02:00"


# ── CR-04: reinicio manual ───────────────────────────────────────────────

def test_crono_reiniciar(app, qtbot):
    """CR-04: REINICIAR vuelve a 00:00:00 y detiene."""
    app.crono_start.click()
    qtbot.waitUntil(lambda: app.crono_time.text() != "00:00:00", timeout=5000)
    app.crono_reset.click()
    assert not app.crono_activo
    assert app.crono_time.text() == "00:00:00"
    assert app.crono_start.text() == "INICIAR"


def test_cambiar_modo_en_marcha_reinicia(app, qtbot):
    """Edge: cambiar de modo en marcha detiene y reinicia."""
    app.crono_start.click()
    qtbot.waitUntil(lambda: app.crono_time.text() != "00:00:00", timeout=5000)
    assert app.crono_activo
    app.crono_mode.setChecked(True)
    app._on_crono_mode(True)
    assert not app.crono_activo
    assert app.crono_time.text() == app._format_crono(60)


# ── CR-05: reset automático al cambiar de ejercicio ──────────────────────

def test_crono_reset_al_cargar_ejercicio(app, qtbot):
    """CR-05: cargar un ejercicio reinicia el crono en marcha."""
    app.crono_start.click()
    qtbot.waitUntil(lambda: app.crono_time.text() != "00:00:00", timeout=5000)
    assert app.crono_activo
    _load_preset(app, "ejemplo_biblioteca.json")
    assert not app.crono_activo
    assert app.crono_time.text() == "00:00:00"
    assert not app.crono_alerta


# ── Unit: formato y ticks sin esperas reales ─────────────────────────────

@pytest.mark.parametrize("segundos,esperado", [
    (0, "00:00:00"),
    (5, "00:00:05"),
    (65, "00:01:05"),
    (3600, "01:00:00"),
    (86399, "23:59:59"),
    (-3, "00:00:00"),
    (3600 * 100, "99:59:59"),  # tope de display
])
def test_format_crono(app, segundos, esperado):
    """Unit: _format_crono produce HH:MM:SS con topes."""
    assert app._format_crono(segundos) == esperado


def test_crono_tick_sin_espera(app):
    """Unit: _crono_tick actualiza el display sin esperar al QTimer."""
    import time as _time
    app.crono_mode.setChecked(False)
    app.crono_activo = True
    app._crono_base = _time.monotonic() - 42
    app._crono_tick()
    assert app.crono_time.text() == "00:00:42"
