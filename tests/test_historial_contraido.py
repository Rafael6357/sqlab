"""Spec historial-contraido — historial colapsado por defecto (HC)."""
from __future__ import annotations


def test_hc01_contraido_al_arrancar(app):
    """HC-01: toggle existe, apagado, lista oculta."""
    assert hasattr(app, "historial_toggle")
    assert app.historial_toggle.isCheckable()
    assert not app.historial_toggle.isChecked()
    assert app.historial_toggle.text() == "VER_HISTORIAL"
    assert app.historial_list.isHidden()


def test_hc02_expandir_contraer(app, qtbot):
    """HC-02: clic expande (OCULTAR_...) y vuelve a contraer."""
    app.historial_toggle.click()
    assert not app.historial_list.isHidden()
    assert app.historial_toggle.text() == "OCULTAR_HISTORIAL"
    app.historial_toggle.click()
    assert app.historial_list.isHidden()
    assert app.historial_toggle.text() == "VER_HISTORIAL"


def test_hc03_limpiar_y_recarga_intactos(app, qtbot):
    """HC-03: limpiar y recarga+ejecuta funcionan (lista oculta o visible)."""
    from PySide6.QtWidgets import QApplication
    app.editor.setPlainText("SELECT * FROM clientes;")
    app.ejecutar_consulta()
    qtbot.wait(50)
    QApplication.processEvents()
    assert app.historial_list.count() >= 1
    app.historial_toggle.click()
    app.btn_clear_hist.click()
    assert app.historial_list.count() == 0
    app.editor.setPlainText("SELECT 1;")
    app.ejecutar_consulta()
    app.historial_list.setCurrentRow(0)
    item = app.historial_list.currentItem()
    assert item is not None
    app._on_historial_clicked(item)
    assert "SELECT 1" in app.editor.toPlainText()
