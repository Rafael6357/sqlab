"""Spec f4-corte-postgres — la UI corre sobre PostgreSQL (FC)."""
from __future__ import annotations

import os

import pytest
from PySide6.QtWidgets import QApplication

from core.pg_engine import PG_BIN_DIR

REQUIERE_PG = not (PG_BIN_DIR and os.path.isfile(os.path.join(PG_BIN_DIR, "initdb.exe")))
salta_sin_pg = pytest.mark.skipif(REQUIERE_PG, reason="sin binarios PG vendoreados")


def _motor_sqlite():
    from core.sqlite_engine import SQLEngine
    return SQLEngine()


def test_fc01_inyeccion_sin_hilo(app):
    """FC-01: con engine inyectado hay preset directo y no hay hilo de arranque."""
    assert not hasattr(app, "_hilo_motor") or app._hilo_motor is None
    assert app._motor_listo is True
    assert set(app.engine.table_names()) >= {"clientes", "pedidos"}


def test_fc01_fallo_sin_binarios(qtbot, monkeypatch):
    """FC-01: sin binarios → diálogo fatal sin crash (PGEngine simulado)."""
    from ui import main_window as mw
    avisos = []
    monkeypatch.setattr(mw, "_show_custom_dialog", lambda *a, **k: avisos.append(a[1]))

    def _boom():
        raise RuntimeError("Sin binarios PostgreSQL vendoreados.")

    monkeypatch.setattr(mw, "PGEngine", _boom)
    w = mw.MainWindow()
    qtbot.addWidget(w)
    w.show()
    qtbot.waitUntil(lambda: "MOTOR NO DISPONIBLE" in w.toast_msg, timeout=10000)
    assert w.engine is None
    assert avisos


def test_fc02_guards_sin_motor(app):
    """FC-02: con motor None, las entradas avisan sin excepción."""
    app.engine = None
    app._motor_listo = False
    app.editor.setPlainText("SELECT 1;")
    app.ejecutar_consulta()
    assert "MOTOR INICIANDO" in app.toast_msg
    app.guardar_sesion()
    assert "MOTOR INICIANDO" in app.toast_msg
    app.exportar_db()
    assert "MOTOR INICIANDO" in app.toast_msg


def test_fc03_labels_sqlite(qtbot):
    """FC-03: con SQLite, etiquetas del dialecto viejo."""
    from core.sqlite_engine import SQLEngine
    from ui.main_window import MainWindow
    w = MainWindow(engine=SQLEngine())
    qtbot.addWidget(w)
    w.show()
    assert w.engine.dialect == "SQLITE3"
    assert "SQLITE3" in w.dialecto_label.text()
    assert "DB: MEMORIA OK" in w.status_db.text()
    w.editor.setPlainText("SELEKT 1;")
    w.ejecutar_consulta()
    assert w.error_title.text() == "ERROR SQL"
    assert "SQLITE3" in w.error_code.text()


@salta_sin_pg
def test_fc03_labels_pg(qtbot, tmp_path):
    """FC-03: con PG, etiquetas del dialecto nuevo (servidor propio aislado)."""
    from core.pg_engine import PGEngine
    from ui.main_window import MainWindow
    eng = PGEngine(base_dir=str(tmp_path))
    try:
        w = MainWindow(engine=eng)
        qtbot.addWidget(w)
        w.show()
        assert eng.dialect == "POSTGRESQL"
        assert "POSTGRESQL" in w.dialecto_label.text()
        assert "DB: PG LOCAL OK" in w.status_db.text()
        w.editor.setPlainText("SELEKT 1;")
        w.ejecutar_consulta()
        assert w.error_title.text() == "ERROR SQL"
        assert "POSTGRESQL" in w.error_code.text()
    finally:
        eng.close()


@salta_sin_pg
def test_fc04_pg_nativo_en_ui(qtbot, tmp_path):
    """FC-04: :: y date_part funcionan en la UI con motor PG (servidor propio)."""
    from core.pg_engine import PGEngine
    from ui.main_window import MainWindow
    eng = PGEngine(base_dir=str(tmp_path))
    try:
        w = MainWindow(engine=eng)
        qtbot.addWidget(w)
        w.show()
        w.editor.setPlainText("SELECT '5'::INTEGER + 1 AS v;")
        w.ejecutar_consulta()
        qtbot.wait(50)
        QApplication.processEvents()
        assert w.resultado_tabla.item(0, 0).text() == "6"
        w.editor.setPlainText("SELECT date_part('year', DATE '2024-05-01') AS y;")
        w.ejecutar_consulta()
        qtbot.wait(50)
        QApplication.processEvents()
        assert w.resultado_tabla.item(0, 0).text() == "2024.0"
    finally:
        eng.close()


def test_fc04_formato_pg_y_decimal():
    """FC-04: keywords PG en el formateador; Decimal alinea a la derecha."""
    from decimal import Decimal

    from PySide6.QtCore import Qt

    from ui.formato_sql import _formatear_sql
    from ui.tablas import _item_grilla
    out = _formatear_sql("select a from t returning b")
    assert "RETURNING" in out
    assert _item_grilla(Decimal("1.5")).textAlignment() == Qt.AlignmentFlag.AlignRight


def test_fc03_close_cierra_motor(app):
    """FC-03: closeEvent cierra el motor (None-safe)."""
    app.close()
    assert not app.engine.connected
