"""Spec autocompletar-con-enter — Enter/Tab acepta la sugerencia."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication


def _con_autocompletado(app, qtbot):
    app.autocomplete_check.setChecked(True)
    qtbot.wait(50)
    QApplication.processEvents()
    assert app._completer is not None


def _escribir_prefijo(app, qtbot, texto="SEL"):
    app.editor.setPlainText(texto)
    app.editor.moveCursor(QTextCursor.MoveOperation.End)
    qtbot.wait(100)
    QApplication.processEvents()


def test_ac01_enter_inserta(app, qtbot):
    """AC-01: popup visible + Enter → inserta sin salto de línea."""
    _con_autocompletado(app, qtbot)
    _escribir_prefijo(app, qtbot)
    assert app._completer.popup().isVisible()
    qtbot.keyClick(app.editor, Qt.Key.Key_Enter)
    qtbot.wait(50)
    QApplication.processEvents()
    assert app.editor.toPlainText() == "SELECT"
    assert "\n" not in app.editor.toPlainText()


def test_ac02_tab_inserta(app, qtbot):
    """AC-02: popup visible + Tab → inserta (no cambia el foco)."""
    _con_autocompletado(app, qtbot)
    _escribir_prefijo(app, qtbot)
    assert app._completer.popup().isVisible()
    qtbot.keyClick(app.editor, Qt.Key.Key_Tab)
    qtbot.wait(50)
    QApplication.processEvents()
    assert app.editor.toPlainText() == "SELECT"


def test_ac03_ctrl_enter_ejecuta(app, qtbot):
    """AC-03: Ctrl+Enter ejecuta aunque haya popup (no inserta)."""
    _con_autocompletado(app, qtbot)
    app.editor.setPlainText("SELECT * FROM clientes")
    app.editor.moveCursor(QTextCursor.MoveOperation.End)
    qtbot.wait(100)
    QApplication.processEvents()
    qtbot.keyClick(app.editor, Qt.Key.Key_Return, Qt.KeyboardModifier.ControlModifier)
    qtbot.wait(100)
    QApplication.processEvents()
    assert "T_EJEC" in app.exec_time.text()
    assert "SELECT" not in app.editor.toPlainText().replace("SELECT * FROM clientes", "")


def test_ac03_escape_cierra_sin_cambios(app, qtbot):
    """AC-03: Escape cierra el popup sin insertar ni cambiar texto."""
    _con_autocompletado(app, qtbot)
    _escribir_prefijo(app, qtbot)
    assert app._completer.popup().isVisible()
    qtbot.keyClick(app.editor, Qt.Key.Key_Escape)
    qtbot.wait(50)
    QApplication.processEvents()
    assert not app._completer.popup().isVisible()
    assert app.editor.toPlainText() == "SEL"


def test_ac04_sin_popup_enter_normal(app, qtbot):
    """AC-04: con AUTOCOMPLETAR apagado, Enter hace salto de línea."""
    app.autocomplete_check.setChecked(False)
    qtbot.wait(50)
    QApplication.processEvents()
    app.editor.setPlainText("SEL")
    app.editor.moveCursor(QTextCursor.MoveOperation.End)
    qtbot.wait(50)
    QApplication.processEvents()
    qtbot.keyClick(app.editor, Qt.Key.Key_Enter)
    assert app.editor.toPlainText() == "SEL\n"
