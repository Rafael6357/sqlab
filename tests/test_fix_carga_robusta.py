"""Spec fix-carga-robusta — sin pérdidas silenciosas al cargar."""
from __future__ import annotations


def test_cr01_json_con_bom(tmp_path):
    """CR-01: JSON con BOM carga igual que sin BOM."""
    from core.session_loader import load_file

    p = tmp_path / "bom.json"
    payload = '{"ejercicio": {"titulo": "T"}, "tablas": [{"nombre": "t", "columnas": [{"nombre": "id", "tipo": "INTEGER"}], "filas": [[1]]}]}'
    p.write_bytes(b"\xef\xbb\xbf" + payload.encode("utf-8"))
    res = load_file(str(p))
    assert res.ok, res.errors
    assert res.tables[0].name == "t"


def test_cr02_headers_case_insensitive_y_comillas():
    """CR-02: 'Nombre'/'nombre' → 'Nombre'/'nombre_2'; 'a\"b' → 'ab'."""
    from core.session_loader import _normalize_headers

    assert _normalize_headers(["Nombre", "nombre", 'a"b', "", ""]) == [
        "Nombre",
        "nombre_2",
        "ab",
        "col4",
        "col5",
    ]


def test_cr03_engine_devuelve_omitidas():
    """CR-03: load_tables informa tablas descartadas."""
    from core.sqlite_engine import Column, SQLEngine, Table

    eng = SQLEngine()
    mala = Table(name="mala", columns=[Column(name="a"), Column(name="A")], rows=[[1, 2]])
    buena = Table(name="buena", columns=[Column(name="id")], rows=[[1]])
    omitidas = eng.load_tables([mala, buena])
    assert omitidas == ["mala"]
    assert eng.table_names() == ["buena"]


def test_cr03_ui_avisa_omitidas(app, monkeypatch):
    """CR-03: la UI avisa con toast si el engine descarta tablas."""
    from core.sqlite_engine import Column, Table
    from core.session_loader import LoadResult

    res = LoadResult(
        ok=True,
        tables=[
            Table(name="ok", columns=[Column(name="id")], rows=[[1]]),
            Table(name="dup", columns=[Column(name="a"), Column(name="A")], rows=[[1, 2]]),
        ],
        errors=[],
    )
    monkeypatch.setattr("ui.main_window._show_custom_dialog", lambda *a, **k: None)
    app._aplicar_resultado(res, "test")
    assert "OMITIDA" in app.toast_msg
    assert "DUP" in app.toast_msg  # _toast mayusculiza


def test_cr04_select_all_entrecomilla(app):
    """CR-04: tabla con espacio → SELECT * FROM \"mis datos\"."""
    from core.sqlite_engine import Column, Table

    app.engine.load_tables([Table(name="mis datos", columns=[Column(name="id")], rows=[[1]])])
    app._refresh_tabla_list()
    app.tabla_list.setCurrentRow(0)
    app.ver_select_all()
    assert app.editor.toPlainText() == 'SELECT * FROM "mis datos";'
