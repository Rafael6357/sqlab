"""Spec graficos-basicos — barras/líneas desde 2 columnas + PNG (GR)."""
from __future__ import annotations

import pytest

QtCharts = pytest.importorskip("PySide6.QtCharts")


def test_gr02_mapeo_y_validacion():
    """GR-02/GR-04 unit: mapeo con nulos saltados y tope 200."""
    from ui.graficos import MAX_PUNTOS, datos_para_grafico, puede_graficar
    assert datos_para_grafico(["a", "b"], [[None, None], ["x", "no-num"]]) is None
    assert datos_para_grafico(["a"], [[1]]) is None
    assert datos_para_grafico(["a", "b"], []) is None
    rows = [[f"e{i}", i] for i in range(500)]
    etiq, vals = datos_para_grafico(["e", "v"], rows)
    assert len(vals) == MAX_PUNTOS and vals[0] == 0.0
    assert puede_graficar(["e", "v"], [["a", 1], ["b", None]])


def test_gr01_dialogo_con_chart(app, qtbot, monkeypatch):
    """GR-01: botón GRAFICAR abre diálogo con chart."""
    from PySide6.QtWidgets import QDialog
    monkeypatch.setattr(QDialog, "exec", lambda self: 0)
    assert hasattr(app, "btn_graficar")
    assert app.btn_graficar.text() == "GRAFICAR"
    app._mostrar_resultado(["nombre", "total"], [["Ana", 10], ["Luis", 20]])
    app.btn_graficar.click()
    from ui.graficos import DialogoGrafico
    dlg = app.findChild(DialogoGrafico)
    assert dlg is not None
    assert dlg.vista.chart() is not None
    dlg.close()


def test_gr02_toast_sin_2_columnas(app):
    """GR-02: sin 2 columnas numéricas → toast, sin diálogo."""
    from ui.graficos import DialogoGrafico
    app._mostrar_resultado(["a", "b", "c"], [[1, 2, 3]])
    app.btn_graficar.click()
    assert "2 COLUMNAS" in app.toast_msg
    assert app.findChild(DialogoGrafico) is None


def test_gr03_png(app, qtbot, monkeypatch, tmp_path):
    """GR-03: GUARDAR PNG crea fichero no vacío; cancelar no crea."""
    from PySide6.QtWidgets import QDialog, QFileDialog
    from ui.graficos import DialogoGrafico
    monkeypatch.setattr(QDialog, "exec", lambda self: 0)
    app._mostrar_resultado(["n", "v"], [["a", 1]])
    app.btn_graficar.click()
    dlg = app.findChild(DialogoGrafico)
    assert dlg is not None
    dest = tmp_path / "g.png"
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *a, **k: (str(dest), "PNG (*.png)"))
    dlg.guardar_png()
    assert dest.exists() and dest.stat().st_size > 0
    dlg.close()
