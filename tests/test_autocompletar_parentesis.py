"""Spec autocompletar-parentesis — funciones con () y cursor dentro."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication


def test_pr01_funcion_con_parentesis_y_cursor(app):
    """PR-01: completar COUNT → 'COUNT()' con cursor dentro."""
    app.editor.setPlainText("COU")
    app.editor.moveCursor(QTextCursor.MoveOperation.End)
    app._insert_completion("COUNT")
    assert app.editor.toPlainText() == "COUNT()"
    assert app.editor.textCursor().position() == len("COUNT(")


def test_pr02_no_funcion_intacta(app):
    """PR-02: completar tabla/keyword no agrega paréntesis."""
    app.editor.setPlainText("clien")
    app.editor.moveCursor(QTextCursor.MoveOperation.End)
    app._insert_completion("clientes")
    assert app.editor.toPlainText() == "clientes"
    app.editor.setPlainText("SEL")
    app.editor.moveCursor(QTextCursor.MoveOperation.End)
    app._insert_completion("SELECT")
    assert app.editor.toPlainText() == "SELECT"


def test_pr03_paren_manual_autocierra(app, qtbot):
    """PR-03: escribir ( sin popup → () con cursor dentro."""
    app.autocomplete_check.setChecked(False)
    qtbot.wait(50)
    QApplication.processEvents()
    app.editor.setPlainText("COUNT")
    app.editor.moveCursor(QTextCursor.MoveOperation.End)
    qtbot.keyClick(app.editor, Qt.Key.Key_ParenLeft)
    qtbot.wait(50)
    QApplication.processEvents()
    assert app.editor.toPlainText() == "COUNT()"
    assert app.editor.textCursor().position() == len("COUNT(")


def test_pr03_paren_con_popup_normal(app, qtbot):
    """PR-03: con popup visible, ( se escribe normal (re-filtra)."""
    app.autocomplete_check.setChecked(True)
    qtbot.wait(50)
    QApplication.processEvents()
    app.editor.setPlainText("COU")
    app.editor.moveCursor(QTextCursor.MoveOperation.End)
    qtbot.wait(100)
    QApplication.processEvents()
    assert app._completer.popup().isVisible()
    qtbot.keyClick(app.editor, Qt.Key.Key_ParenLeft)
    qtbot.wait(50)
    QApplication.processEvents()
    assert app.editor.toPlainText() == "COU("
