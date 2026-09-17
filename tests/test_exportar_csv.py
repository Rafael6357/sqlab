"""Spec exportar-resultado-csv — guardar el resultado en .csv para Excel."""
from __future__ import annotations

import csv


def _exportar(app, monkeypatch, destino):
    from PySide6.QtWidgets import QFileDialog
    monkeypatch.setattr(
        QFileDialog, "getSaveFileName",
        lambda *a, **k: (str(destino), "CSV (*.csv)"),
    )
    app.exportar_resultado_csv()
    return destino


def test_ex01_boton_existe(app):
    """EX-01: botón EXPORTAR CSV en la cabecera de resultados."""
    assert hasattr(app, "btn_exportar")
    assert app.btn_exportar.text() == "EXPORTAR CSV"


def test_ex02_exporta_todo_aunque_grilla_topada(app, monkeypatch, tmp_path):
    """EX-02: 6000 filas → fichero con cabecera + 6000 (grilla muestra 5000)."""
    cols = ["id", "nombre"]
    rows = [[i, f"n{i}"] for i in range(6000)]
    app._mostrar_resultado(cols, rows)
    assert app.resultado_tabla.rowCount() == 5000
    dest = _exportar(app, monkeypatch, tmp_path / "res.csv")
    with open(str(dest), encoding="utf-8-sig") as fh:
        leidas = list(csv.reader(fh))
    assert leidas[0] == ["id", "nombre"]
    assert len(leidas) == 6001
    assert leidas[6000] == ["5999", "n5999"]


def test_ex03_none_como_vacio_y_excel_bom(app, monkeypatch, tmp_path):
    """EX-03/04: None → vacío; fichero con BOM para Excel."""
    app._mostrar_resultado(["a", "b"], [[None, "x"], ["áé", None]])
    dest = _exportar(app, monkeypatch, tmp_path / "r.csv")
    crudo = dest.read_bytes()
    assert crudo.startswith(b"\xef\xbb\xbf"), "sin BOM utf-8-sig"
    with open(str(dest), encoding="utf-8-sig") as fh:
        leidas = list(csv.reader(fh))
    assert leidas == [["a", "b"], ["", "x"], ["áé", ""]]
    assert "None" not in crudo.decode("utf-8-sig")


def test_ex04_entrecomillado_estandar(app, monkeypatch, tmp_path):
    """Comas/comillas/saltos → QUOTE_MINIMAL válido."""
    app._mostrar_resultado(["t"], [['hola, "mundo"\nfin']])
    dest = _exportar(app, monkeypatch, tmp_path / "q.csv")
    with open(str(dest), encoding="utf-8-sig") as fh:
        assert list(csv.reader(fh)) == [["t"], ['hola, "mundo"\nfin']]


def test_ex05_cancelar_no_hace_nada(app, monkeypatch, tmp_path):
    """EX-05: cancelar → sin fichero ni toast de éxito."""
    from PySide6.QtWidgets import QFileDialog
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *a, **k: ("", ""))
    app._mostrar_resultado(["a"], [["1"]])
    antes = app.toast_msg
    app.exportar_resultado_csv()
    assert not (tmp_path / "resultado.csv").exists()
    assert app.toast_msg == antes


def test_ex06_sin_resultados_toast(app, monkeypatch):
    """EX-06: sin resultado → toast, sin diálogo."""
    from PySide6.QtWidgets import QFileDialog
    llamadas = []
    monkeypatch.setattr(
        QFileDialog, "getSaveFileName",
        lambda *a, **k: (llamadas.append(1), ("x",))[1],
    )
    app._limpiar_resultado()
    app._ultimo_resultado = ([], [])
    app.exportar_resultado_csv()
    assert llamadas == []
    assert "NADA QUE EXPORTAR" in app.toast_msg
