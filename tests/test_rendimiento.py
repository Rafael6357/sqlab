"""Spec rendimiento-tablas-grandes — topes de render, muestreo, aviso y lote."""
from __future__ import annotations

from PySide6.QtWidgets import QDialog, QHeaderView, QPushButton


def _tabla(n_filas: int, n_cols: int = 4):
    from core.sqlite_engine import Column, Table
    cols = [Column(name=f"c{i}", type="TEXT") for i in range(n_cols)]
    rows = [[f"v{r}_{c}_texto" for c in range(n_cols)] for r in range(n_filas)]
    return Table(name="grande", columns=cols, rows=rows)


def test_rg01_visor_topa_2000_con_aviso(app, qtbot):
    """RG-01: visor renderiza 2000 y conserva las 2500 filas de origen."""
    tabla = _tabla(2500)
    app._refresh_dump(tabla)
    qtbot.wait(30)
    assert app.visor_tabla.rowCount() == 2000
    assert len(tabla.rows) == 2500
    assert not hasattr(app, "row_count_label")


def test_rg02_resultado_topa_5000_con_aviso(app, qtbot):
    """RG-02: resultado renderiza 5000, badge y toast con el total."""
    cols = ["a", "b"]
    rows = [[f"v{r}", "x"] for r in range(6000)]
    app._mostrar_resultado(cols, rows)
    qtbot.wait(30)
    assert app.resultado_tabla.rowCount() == 5000
    assert app.row_badge.text() == "6000 FILAS"
    assert "6000" in app.exec_time.text() and "5000" in app.exec_time.text()


def test_rg03_sin_topes_comportamiento_intacto(app):
    """RG-03: tablas chicas sin sufijos ni cambios, y sin etiqueta de conteo."""
    tabla = _tabla(3)
    app._refresh_dump(tabla)
    assert app.visor_tabla.rowCount() == 3
    assert len(tabla.rows) == 3
    assert not hasattr(app, "row_count_label")
    app._mostrar_resultado(["a"], [["1"], ["2"]])
    assert app.resultado_tabla.rowCount() == 2
    assert app.row_badge.text() == "2 FILAS"


def test_rg04_anchos_por_muestreo(app, qtbot):
    """RG-04 (actualizado por AE): Interactive con tope en medición; el hueco lo reparte AE."""
    app._refresh_dump(_tabla(5000, 10))
    qtbot.wait(30)
    header = app.visor_tabla.horizontalHeader()
    assert header.sectionResizeMode(0) == QHeaderView.ResizeMode.Interactive
    anchos = [header.sectionSize(i) for i in range(10)]
    assert all(a <= 300 for a in anchos)
    assert not header.stretchLastSection()
    # El muestreo cubre cabecera: columna con header largo no colapsa
    assert all(a > 0 for a in anchos)


def test_rg05_confirmar_archivo_grande_cancela(app, monkeypatch, tmp_path):
    """RG-05: >50 MB pide confirmación; cancelar no carga nada."""
    from ui.main_window import MainWindow
    assert MainWindow.AVISO_MB == 50
    # Archivo chico → True sin diálogo
    chico = tmp_path / "chico.csv"
    chico.write_text("a\n1\n", encoding="utf-8")
    assert app._confirmar_archivo_grande([str(chico)]) is True
    # Archivo grande simulado (sparse) → diálogo; CANCELAR → False
    grande = tmp_path / "grande.csv"
    with open(str(grande), "wb") as fh:
        fh.truncate(51 * 1024 * 1024)

    def fake_exec(self):
        for btn in self.findChildren(QPushButton):
            if btn.text() == "CANCELAR":
                btn.click()
                break
        return QDialog.DialogCode.Rejected

    monkeypatch.setattr(QDialog, "exec", fake_exec)
    assert app._confirmar_archivo_grande([str(grande)]) is False


def test_rg05_confirmar_archivo_grande_acepta(app, monkeypatch, tmp_path):
    """Aceptar en el diálogo → True."""
    grande = tmp_path / "g.csv"
    with open(str(grande), "wb") as fh:
        fh.truncate(51 * 1024 * 1024)

    def fake_exec(self):
        for btn in self.findChildren(QPushButton):
            if btn.text() == "CARGAR":
                btn.click()
                break
        return QDialog.DialogCode.Accepted

    monkeypatch.setattr(QDialog, "exec", fake_exec)
    assert app._confirmar_archivo_grande([str(grande)]) is True


def test_rg06_executemany_carga_todo(tmp_path):
    """RG-06: lote rápido carga todas las filas íntegras."""
    from core.sqlite_engine import SQLEngine
    from core.session_loader import load_file

    p = tmp_path / "lote.csv"
    with open(str(p), "w", encoding="utf-8") as fh:
        fh.write("id,nombre\n")
        for i in range(5000):
            fh.write(f"{i},nombre_{i}\n")
    res = load_file(str(p))
    assert res.ok, res.errors
    eng = SQLEngine()
    eng.load_tables(res.tables)
    assert eng.tables["lote"].rows is not None
    r = eng.execute("SELECT COUNT(*) FROM lote")
    assert r.rows == [[5000]]
    r2 = eng.execute("SELECT nombre FROM lote WHERE id = 4999")
    assert r2.rows == [["nombre_4999"]]
