"""Spec compat-postgres — :: reescrito + hints de dialecto + regresión."""
from __future__ import annotations


def _eng():
    from core.sqlite_engine import SQLEngine
    e = SQLEngine()
    assert e.load_tables([]) == []
    return e


def _eng_tienda():
    from core.session_loader import load_file
    from core.sqlite_engine import SQLEngine
    import os
    base = os.path.join(os.path.dirname(__file__), "..", "examples", "ejemplo_tienda.json")
    res = load_file(os.path.normpath(base))
    assert res.ok, res.errors
    e = SQLEngine()
    e.load_tables(res.tables)
    return e


def test_pg01_rewrite_directo():
    """PG-01 unit: :: fuera de literales se vuelve CAST."""
    from core.sqlite_engine import _reescribir_cast_postgres as rw
    assert rw("SELECT '5'::INTEGER") == "SELECT CAST('5' AS INTEGER)"
    assert rw('SELECT "col"::TEXT') == 'SELECT CAST("col" AS TEXT)'
    assert rw("SELECT (a+b)::REAL") == "SELECT CAST((a+b) AS REAL)"
    assert rw("SELECT x::VARCHAR(10)") == "SELECT CAST(x AS VARCHAR(10))"


def test_pg01_e2e():
    """PG-01 e2e: '5'::INTEGER + 1 = 6."""
    e = _eng_tienda()
    r = e.execute("SELECT '5'::INTEGER + 1 AS v")
    assert r.ok, r.error
    assert r.rows == [[6]]


def test_pg02_literales_intactos():
    """PG-02: :: dentro de strings/comentarios no se toca."""
    from core.sqlite_engine import _reescribir_cast_postgres as rw
    assert rw("SELECT 'a::b'") == "SELECT 'a::b'"
    assert rw("SELECT 'x' -- nota ::int\nFROM t") == "SELECT 'x' -- nota ::int\nFROM t"
    assert rw("SELECT 1 /* c::t */") == "SELECT 1 /* c::t */"
    e = _eng_tienda()
    r = e.execute("SELECT 'a::b' AS v")
    assert r.ok and r.rows == [["a::b"]]


def test_pg03_hints_dialecto():
    """PG-03: date_part/now/ILIKE/USING calificado → sugerencia SQLite."""
    from core.error_friendly import friendly_error
    h = friendly_error("no such function: date_part", [], "SELECT date_part('year', f) FROM t")
    assert "STRFTIME" in h
    h = friendly_error("no such function: now", [], "SELECT now()")
    assert "DATE(" in h and "now" in h.lower()
    h = friendly_error("syntax error", [], "SELECT * FROM a ILIKE 'x'")
    assert "LIKE" in h
    h = friendly_error("syntax error", [], "SELECT * FROM a JOIN b USING a.id")
    assert "USING" in h


def test_pg03_sin_query_intacto():
    """PG-03: sin query, friendly_error como antes."""
    from core.error_friendly import friendly_error
    assert "COUNT" in friendly_error("no such function: xxx")


def test_pg04_cast_y_using():
    """PG-04: CAST y USING simple funcionan (regresión)."""
    e = _eng_tienda()
    r = e.execute("SELECT CAST('123' AS INTEGER) + 1 AS v")
    assert r.ok and r.rows == [[124]]
    r = e.execute("SELECT c1.nombre FROM clientes c1 INNER JOIN clientes c2 USING (id) LIMIT 1")
    assert r.ok, r.error
