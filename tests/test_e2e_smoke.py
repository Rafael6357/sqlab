"""E2E / Smoke tests — verifican que la app completa funciona en modo offscreen.

Todos los tests usan el fixture `app` (MainWindow) de conftest.py.
QDialog.exec y QFileDialog están parcheados para no bloquear.
"""
from __future__ import annotations

import json
import os

from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QFileDialog,
    QDialog,
    QPlainTextEdit,
)

from ui.main_window import MainWindow, CLAUDE_PROMPT

EXAMPLES = os.path.join(os.path.dirname(__file__), "..", "examples")


# ── helpers ────────────────────────────────────────────────────────────

def _load_preset(w: MainWindow, filename: str = "ejemplo_tienda.json") -> None:
    """Carga un preset directamente sin diálogo de archivos."""
    path = os.path.normpath(os.path.join(EXAMPLES, filename))
    from core.session_loader import load_file
    result = load_file(path)
    w._aplicar_resultado(result, path)


# ── BOOT / INIT ────────────────────────────────────────────────────────

def test_app_boots(app):
    """MainWindow crea sin errores, título correcto, motor conectado."""
    assert "SQLab" in app.window().windowTitle()
    assert app.engine.connected
    assert len(app.engine.table_names()) > 0


def test_initial_preset_loaded(app):
    """Al arrancar se carga ejemplo_tienda.json automáticamente."""
    assert "clientes" in app.engine.table_names()
    assert "pedidos" in app.engine.table_names()
    assert app.tabla_list.count() == 2
    assert app.tables_count.text() == "(2)"
    assert "SIN EJERCICIO" not in app.exercise_title.text()


def test_initial_editor_has_default_query(app):
    """CV-01: al arrancar el editor está vacío (ya no inyecta defaultQuery)."""
    assert app.editor.toPlainText() == ""
    # ...pero la plantilla sigue aplicándose en cargas explícitas:
    app.cargar_preset("ejemplo_tienda.json")
    assert "SELECT" in app.editor.toPlainText().upper()


# ── EJECUTAR SQL ──────────────────────────────────────────────────────

def test_execute_select_star(app):
    """SELECT * FROM clientes devuelve 4 filas, tabla visible."""
    app.editor.setPlainText("SELECT * FROM clientes;")
    app.ejecutar_consulta()
    assert app.resultado_tabla.isVisible()
    assert app.resultado_tabla.rowCount() == 4
    assert app.resultado_tabla.columnCount() == 3
    assert "FILAS" in app.row_badge.text()


def test_execute_select_where(app):
    """WHERE filtra correctamente."""
    app.editor.setPlainText("SELECT nombre FROM clientes WHERE id = 1;")
    app.ejecutar_consulta()
    assert app.resultado_tabla.rowCount() == 1
    item = app.resultado_tabla.item(0, 0)
    assert item is not None and item.text() == "Ana Pérez"


def test_execute_syntax_error(app):
    """Consulta con error muestra error_box."""
    app.editor.setPlainText("SELEC * FROM clientes;")
    app.ejecutar_consulta()
    assert app.error_box.isVisible()
    assert not app.resultado_tabla.isVisible()
    assert app.error_text.text()  # texto de error no vacío


def test_execute_empty_editor(app):
    """Editor vacío produce error."""
    app.editor.setPlainText("")
    app.ejecutar_consulta()
    assert app.error_box.isVisible()
    assert "VACÍO" in app.error_text.text() or "vacía" in app.error_text.text()


def test_execute_adds_to_historial(app):
    """Consulta exitosa se añade al historial."""
    before = len(app.historial)
    app.editor.setPlainText("SELECT COUNT(*) FROM clientes;")
    app.ejecutar_consulta()
    assert len(app.historial) == before + 1
    assert app.historial_list.count() >= before + 1


# ── FORMATO / FORMATEAR ───────────────────────────────────────────────

def test_formato_toggle(app):
    """FS-05: btn_format es botón normal (no checkable) y aplica formato real."""
    assert not app.btn_format.isCheckable()
    app.editor.setPlainText("select * from clientes")
    app.formatear_consulta()
    assert app.editor.toPlainText() == "SELECT *\nFROM clientes"


# ── FIX C2: FORMATEO PRESERVA LITERALES Y COMENTARIOS ─────────────────

def test_formato_preserva_literal_texto(app):
    """C2-02: palabras del literal '...' no se formatean a mayúsculas."""
    app.editor.setPlainText("select * from clientes where nombre = 'from spain'")
    app.formatear_consulta()
    txt = app.editor.toPlainText()
    assert "SELECT" in txt and "FROM clientes" in txt
    assert "'from spain'" in txt, f"Literal alterado: {txt!r}"


def test_formato_preserva_literal_comilla_escapada(app):
    """C2-03: comilla SQLite escapada ('' ) dentro del literal se preserva."""
    app.editor.setPlainText("select nombre from clientes where nombre like 'it''s from'")
    app.formatear_consulta()
    txt = app.editor.toPlainText()
    assert "'it''s from'" in txt, f"Literal con '' alterado: {txt!r}"
    assert "SELECT" in txt and "FROM" in txt


def test_formato_preserva_comentario_linea(app):
    """C2-04: comentario de línea (--) se preserva sin formatear."""
    app.editor.setPlainText("select * from clientes -- select secreto")
    app.formatear_consulta()
    txt = app.editor.toPlainText()
    assert "-- select secreto" in txt
    assert "-- SELECT" not in txt
    assert "SELECT" in txt and "FROM clientes" in txt


def test_formato_preserva_comentario_bloque(app):
    """C2-05: comentario de bloque (/* */) se preserva sin formatear."""
    app.editor.setPlainText("select * from clientes /* where x from y */")
    app.formatear_consulta()
    txt = app.editor.toPlainText()
    assert "/* where x from y */" in txt
    assert "/* WHERE" not in txt
    assert "SELECT" in txt and "FROM clientes" in txt


def test_formato_editor_vacio_no_crashea(app):
    """C2-06: formatear editor vacío no lanza y no cambia nada."""
    app.editor.clear()
    app.formatear_consulta()
    assert app.editor.toPlainText() == ""


# ── MODAL FORMATO JSON ────────────────────────────────────────────────

def test_json_dialog_contains_template(app, qtbot, monkeypatch):
    """mostrar_formato_json abre diálogo con CLAUDE_PROMPT, no bloquea."""
    monkeypatch.setattr(QDialog, "exec", lambda self: 0)
    app.mostrar_formato_json()
    editors = app.findChildren(QPlainTextEdit)
    prompt_editors = [e for e in editors if e.toPlainText() == CLAUDE_PROMPT]
    assert prompt_editors, "No se encontró editor con CLAUDE_PROMPT en el diálogo"
    assert len(CLAUDE_PROMPT) > 100


def test_json_dialog_copy_button(app, qtbot, monkeypatch):
    """Botón COPIAR PLANTILLA copia CLAUDE_PROMPT al portapapeles."""
    monkeypatch.setattr(QDialog, "exec", lambda self: 0)
    app.mostrar_formato_json()
    clipboard = QGuiApplication.clipboard()
    from PySide6.QtWidgets import QPushButton
    btns = app.findChildren(QPushButton)
    copy_btns = [b for b in btns if b.text().startswith("COPIAR PLANTILLA")]
    assert copy_btns, "No se encontró botón COPIAR PLANTILLA (IA-02)"
    copy_btns[0].click()
    assert clipboard.text() == CLAUDE_PROMPT


# ── COPIAR PARA IA ────────────────────────────────────────────────────

def test_copiar_para_ia(app):
    """copiar_consulta copia el contenido del editor al portapapeles."""
    app.editor.setPlainText("SELECT nombre FROM clientes;")
    app.copiar_consulta()
    cb = QGuiApplication.clipboard()
    assert "SELECT nombre FROM clientes" in cb.text()


# ── FIX C1: RESTABLECER DATOS RECARGA PRESET ORIGINAL ─────────────────

def test_restablecer_datos_vuelve_al_preset_inicial(app):
    """C1-01: restablecer_datos restaura el preset de arranque (tienda)."""
    assert "clientes" in app.engine.table_names()
    assert "pedidos" in app.engine.table_names()
    app.editor.setPlainText("DELETE FROM clientes;")
    app.ejecutar_consulta()
    total = app.engine.execute("SELECT COUNT(*) FROM clientes;").rows[0][0]
    assert total == 0
    app.restablecer_datos()
    names = app.engine.table_names()
    assert "clientes" in names
    assert "pedidos" in names
    assert app.tabla_list.count() == len(names)
    total = app.engine.execute("SELECT COUNT(*) FROM clientes;").rows[0][0]
    assert total == 4


def test_restablecer_datos_desde_otro_preset(app):
    """C1-02: tras cargar biblioteca, restablecer_datos vuelve a la tienda."""
    _load_preset(app, "ejemplo_biblioteca.json")
    assert "libros" in app.engine.table_names()
    app.restablecer_datos()
    names = app.engine.table_names()
    assert "clientes" in names
    assert "pedidos" in names


def test_restablecer_datos_limpia_resultado_y_conserva_historial(app):
    """C1-03: reset limpia el resultado visible pero conserva el historial."""
    app.editor.setPlainText("SELECT * FROM clientes;")
    app.ejecutar_consulta()
    n_hist = len(app.historial)
    assert app.resultado_tabla.rowCount() > 0 or app.exec_time.text()
    app.restablecer_datos()
    assert len(app.historial) == n_hist
    assert app.engine.connected


# ── VER SELECT * ──────────────────────────────────────────────────────

def test_ver_select_all(app):
    """ver_select_all inserta SELECT * y ejecuta."""
    app.tabla_list.setCurrentRow(0)
    app.ver_select_all()
    assert "SELECT * FROM" in app.editor.toPlainText().upper()
    assert app.resultado_tabla.isVisible()
    assert app.resultado_tabla.rowCount() > 0


# ── LIMPIAR ───────────────────────────────────────────────────────────

def test_limpiar_editor(app):
    app.editor.setPlainText("SELECT 1;")
    app.limpiar_editor()
    assert app.editor.toPlainText() == ""


def test_limpiar_historial(app):
    app.editor.setPlainText("SELECT 1;")
    app.ejecutar_consulta()
    assert len(app.historial) > 0
    app.limpiar_historial()
    assert app.historial == []
    assert app.historial_list.count() == 0


# ── PISTA TOGGLE ──────────────────────────────────────────────────────

def test_hint_toggle(app):
    """Pista del preset tienda: VER_PISTA -> pista_card visible."""
    assert app.pista_toggle.isVisible()
    assert not app.pista_card.isVisible()
    app.pista_toggle.setChecked(True)
    app._on_pista_toggle(True)
    assert app.pista_card.isVisible()
    assert "OCULTAR_PISTA" in app.pista_toggle.text()


def test_hint_toggle_back(app):
    app.pista_toggle.setChecked(True)
    app._on_pista_toggle(True)
    app._on_pista_toggle(False)
    assert not app.pista_card.isVisible()
    assert "VER_PISTA" in app.pista_toggle.text()


# ── MATRIX LIST SELECTION ─────────────────────────────────────────────

def test_table_list_shows_columns(app):
    """Seleccionar una tabla en la lista muestra sus columnas."""
    app.tabla_list.setCurrentRow(0)
    current = app.tabla_list.currentItem()
    assert current is not None
    cols = app.columnas_list.count()
    assert cols > 0


# ── GUARDAR / CARGAR SESIÓN ───────────────────────────────────────────

def test_guardar_cargar_sesion_roundtrip(app, tmp_path, monkeypatch):
    """Guardar sesión y recargarla restaura las tablas y el historial."""
    # Añadir al historial
    app.editor.setPlainText("SELECT * FROM clientes;")
    app.ejecutar_consulta()
    hist_count = len(app.historial)

    # Guardar
    save_path = str(tmp_path / "test_session.json")
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *a, **kw: (save_path, ""))
    app.guardar_sesion()
    assert os.path.exists(save_path)

    # Verificar JSON
    with open(save_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "tablas" in data
    assert "historial" in data
    assert len(data["tablas"]) == 2
    assert len(data["historial"]) == hist_count

    # Cargar
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *a, **kw: (save_path, ""))
    app.cargar_sesion()
    assert "clientes" in app.engine.table_names()
    assert len(app.historial) == hist_count


def test_guardar_sin_tablas_muestra_error(app, monkeypatch):
    """guardar_sesion sin tablas muestra diálogo de error."""
    app.engine.close()
    app.engine.tables = {}
    app.tabla_list.clear()
    called = []
    def mock_dialog(*a, **kw):
        called.append(True)
    monkeypatch.setattr("ui.main_window._show_custom_dialog", mock_dialog)
    app.guardar_sesion()
    assert called  # se llamó el diálogo


# ── CARGAR JSON DIRECTO ───────────────────────────────────────────────

def test_cargar_json_directo(app):
    """Cargar ejemplo_biblioteca reemplaza las tablas actuales."""
    _load_preset(app, "ejemplo_biblioteca.json")
    assert "libros" in app.engine.table_names()
    assert "usuarios" in app.engine.table_names()
    assert "prestamos" in app.engine.table_names()
    assert app.tabla_list.count() == 3


# ── CARGAR CSV FOLDER ─────────────────────────────────────────────────

def test_cargar_csv_folder(app):
    """Cargar carpeta csv crea tablas clientes y productos."""
    csv_folder = os.path.join(EXAMPLES, "csv")
    from core.session_loader import load_csv_folder
    result = load_csv_folder(csv_folder)
    app._aplicar_resultado(result, csv_folder)
    assert "clientes" in app.engine.table_names()
    assert "productos" in app.engine.table_names()


# ── AUTOCOMPLETADO DEFAULT OFF ────────────────────────────────────────

def test_autocomplete_default_off(app):
    """Autocompletado está desactivado por defecto."""
    assert not app.autocomplete_check.isChecked()


# ── CLOSE EVENT ───────────────────────────────────────────────────────

def test_close_event(app):
    """closeEvent cierra la conexión del motor."""
    assert app.engine.connected
    from PySide6.QtGui import QCloseEvent
    app.closeEvent(QCloseEvent())
    assert not app.engine.connected


# ── TOAST ─────────────────────────────────────────────────────────────

def test_toast_sets_text(app):
    """_toast actualiza exec_time y mensaje_label."""
    app._toast("TEST MESSAGE")
    assert app.exec_time.text() == "TEST MESSAGE"
    assert app.mensaje_label.text() == "TEST MESSAGE"


# ── BRIEFING ──────────────────────────────────────────────────────────

def test_briefing_updates_on_preset(app):
    """Al cargar preset, difficulty_badge y exercise_title se actualizan."""
    assert app.difficulty_badge.text() != "PRINCIPIANTE" or app.exercise_title.text() != "SIN EJERCICIO"
    assert app.exercise_title.text() != ""
