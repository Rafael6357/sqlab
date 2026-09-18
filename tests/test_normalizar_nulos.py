"""Spec normalizar-nulos-csv-excel — paridad con pandas na_values."""
from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QApplication


def _make_xlsx(path: Path, rows: list[list]):
    import openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Hoja1"
    for r in rows:
        ws.append(r)
    wb.save(str(path))


def test_nn01_csv_marcadores_como_none(tmp_path):
    """NN-01: vacíos, espacios, -, NA, NULL, null, NaN → None."""
    from core.session_loader import load_file

    p = tmp_path / "nulos.csv"
    p.write_text(
        "a,b,c,d,e,f,g\n"
        ", ,-,NA,NULL,null,NaN\n",
        encoding="utf-8",
    )
    res = load_file(str(p))
    assert res.ok, res.errors
    assert res.tables[0].rows == [[None, None, None, None, None, None, None]]


def test_nn01_csv_marcador_con_espacios(tmp_path):
    """NN-01: ' NA ' (con espacios alrededor) también es None."""
    from core.session_loader import load_file

    p = tmp_path / "esp.csv"
    p.write_text("a,b\n NA ,x\n", encoding="utf-8")
    res = load_file(str(p))
    assert res.ok, res.errors
    assert res.tables[0].rows == [[None, "x"]]


def test_nn02_datos_reales_intactos(tmp_path):
    """NN-02: ' x ', 'N/A', 0 y números se conservan."""
    from core.session_loader import load_file

    p = tmp_path / "datos.csv"
    p.write_text("a,b,c,d\n x ,N/A,0,2.5\n", encoding="utf-8")
    res = load_file(str(p))
    assert res.ok, res.errors
    assert res.tables[0].rows == [[" x ", "N/A", "0", "2.5"]]


def test_nn03_fila_corta_rellena_none(tmp_path):
    """NN-03: fila corta → relleno None (no '')."""
    from core.session_loader import load_file

    p = tmp_path / "corta.csv"
    p.write_text("a,b,c\n1,2\n", encoding="utf-8")
    res = load_file(str(p))
    assert res.ok, res.errors
    assert res.tables[0].rows == [["1", "2", None]]


def test_nn01_xlsx_marcadores_como_none(tmp_path):
    """NN-01 en Excel: '-', 'NA', ' ' → None; números intactos."""
    from core.session_loader import load_file

    p = tmp_path / "nulos.xlsx"
    _make_xlsx(p, [["a", "b", "c", "d"], ["-", "NA", " ", 5]])
    res = load_file(str(p))
    assert res.ok, res.errors
    assert res.tables[0].rows == [[None, None, None, 5]]


def test_nn04_json_respeta_strings(tmp_path):
    """NN-04: JSON con 'NA' explícito no se toca."""
    import json

    from core.session_loader import load_file

    p = tmp_path / "e.json"
    payload = {
        "tablas": [
            {
                "nombre": "t",
                "columnas": [{"nombre": "a", "tipo": "TEXT"}],
                "filas": [["NA"]],
            }
        ]
    }
    p.write_text(json.dumps(payload), encoding="utf-8")
    res = load_file(str(p))
    assert res.ok, res.errors
    assert res.tables[0].rows == [["NA"]]


def test_nn01_e2e_visor_pinta_null(tmp_path, app, qtbot):
    """NN-01 E2E: CSV con ' ' → visor muestra NULL."""
    from core.session_loader import load_tablas_folder

    folder = tmp_path / "finlay"
    folder.mkdir()
    (folder / "pacientes.csv").write_text("edad,nota\n30, \n,alta\n", encoding="utf-8")
    res = load_tablas_folder(str(folder))
    assert res.ok, res.errors
    app.engine.load_tables(res.tables)
    tabla = res.tables[0]
    app._refresh_dump(tabla)
    qtbot.wait(50)
    QApplication.processEvents()
    assert app.visor_tabla.item(0, 1).text() == "NULL"
    assert app.visor_tabla.item(1, 0).text() == "NULL"
    assert app.visor_tabla.item(0, 0).text() == "30"
