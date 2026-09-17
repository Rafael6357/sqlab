"""Fixtures compartidos para la suite E2E/SMOKE de SQLab.

Aísla QSettings en un directorio temporal y crea MainWindow en modo offscreen.
Vincula cada test a su spec en specs/ via pytest marks (ver AGENTS.md Metodología).
"""
from __future__ import annotations

import os
import sys

# Asegurar que los imports de la app son accesibles
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Forzar offscreen antes de que Qt arranque
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtCore import QSettings


# ── Vinculación tests → specs ──────────────────────────────────────────────

# Módulo de test → spec ID (coincide con specs/<id>.md)
_SPEC_MAP: dict[str, str] = {
    "test_sqlite_engine": "sqlite-engine",
    "test_error_friendly": "error-friendly",
    "test_session_loader": "session-loader",
    "test_e2e_smoke": "ui-main-window",
    "test_cronometro": "cronometro-ejercicio",
    "test_icono": "icono-ejecutable",
    "test_fix_matriz": "fix-matriz-resultados",
    "test_carga_tablas": "carga-tablas-excel-csv",
    "test_ejemplos_empaquetados": "fix-ejemplos-empaquetados",
    "test_carga_archivos": "carga-tablas-archivos",
    "test_formato_sql": "formato-sql-real",
    "test_ui_nombres": "ui-nombres-estado",
}


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Agrega pytest.mark.spec('...') automáticamente a cada test según su módulo."""
    for item in items:
        module_name = item.module.__name__.rsplit(".", 1)[-1]
        spec_id = _SPEC_MAP.get(module_name)
        if spec_id:
            item.add_marker(pytest.mark.spec(spec_id))


# ── QSettings aislado (evita contaminar el registry/INI real) ──────────

@pytest.fixture(autouse=True)
def _isolated_settings(tmp_path, monkeypatch):
    """Cada test obtiene un QSettings IniFormat apuntando a tmp_path."""
    QSettings.setDefaultFormat(QSettings.Format.IniFormat)
    QSettings.setPath(QSettings.Format.IniFormat, QSettings.Scope.UserScope, str(tmp_path))
    # Forzar organización/app nuevas para aislamiento
    s = QSettings("SQLTestOrg", "SQLTestSuite")
    s.clear()
    yield s
    s.clear()


# ── MainWindow fixture ─────────────────────────────────────────────────

@pytest.fixture
def app(qtbot):
    """Crea una MainWindow en offscreen, la muestra y la cierra al finalizar."""
    from ui.main_window import MainWindow
    w = MainWindow()
    qtbot.addWidget(w)
    w.show()
    return w
