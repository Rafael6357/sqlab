"""Spec fix-multi-sentencia — scripts con varias sentencias."""
from __future__ import annotations

import pytest


@pytest.fixture
def eng():
    from core.sqlite_engine import Column, SQLEngine, Table
    e = SQLEngine()
    e.load_tables([Table(name="dummy", columns=[Column(name="a")], rows=[[0]])])
    return e


def test_ms01_muestra_ultimo_resultado(eng):
    """MS-01: varias sentencias → último resultado."""
    r = eng.execute("SELECT 1; SELECT 2;")
    assert r.error == "", r.error
    assert r.rows == [[2]]


def test_ms02_script_ddl_dml_select(eng):
    """MS-02: CREATE + INSERT + SELECT encadenados."""
    r = eng.execute("CREATE TABLE m (a INTEGER); INSERT INTO m VALUES (7); SELECT * FROM m;")
    assert r.error == "", r.error
    assert r.rows == [[7]]


def test_ms03_error_amable_sin_crash(eng):
    """MS-03: falla la 2ª → error amable, sin excepción."""
    r = eng.execute("SELECT 1; SELEKT 2;")
    assert r.error != ""


def test_ms04_puntoycoma_en_literal_no_parte(eng):
    """MS-04: ';' dentro de literal no divide."""
    r = eng.execute("SELECT 'a;b'; SELECT 2;")
    assert r.error == "", r.error
    assert r.rows == [[2]]


def test_ms04_puntoycoma_en_comentario_no_parte(eng):
    r = eng.execute("SELECT 1 -- comentario;\n; SELECT 3;")
    assert r.error == "", r.error
    assert r.rows == [[3]]


def test_ms05_una_sentencia_intacta(eng):
    """MS-05: comportamiento de sentencia única intacto."""
    from core.sqlite_engine import Column, Table
    eng.load_tables([Table(name="t", columns=[Column(name="a", type="INTEGER")], rows=[[5]])])
    r = eng.execute("SELECT * FROM t;")
    assert r.rows == [[5]]


def test_ms_e2e_sin_crash_y_muestra_ultimo(app):
    """E2E: el editor acepta scripts y muestra el último resultado."""
    app.editor.setPlainText("SELECT 1; SELECT 2;")
    app.ejecutar_consulta()
    assert app.resultado_tabla.rowCount() == 1
    assert app.resultado_tabla.item(0, 0).text() == "2"
    assert not app.error_box.isVisible()
