"""Spec pg-engine — motor PostgreSQL embebido (PE). Se salta sin binarios."""
from __future__ import annotations

import os
import shutil

import pytest

from core.pg_engine import PG_BIN_DIR, PGEngine

REQUIERE_PG = not (PG_BIN_DIR and os.path.isfile(os.path.join(PG_BIN_DIR, "initdb.exe")))
salta_sin_pg = pytest.mark.skipif(REQUIERE_PG, reason="sin binarios PG vendoreados")


def _tablas_demo():
    from core.sqlite_engine import Column, Table
    return [
        Table(name="clientes", columns=[Column("id", "INTEGER"), Column("nombre", "TEXT"), Column("vip", "BOOLEAN")],
              rows=[[1, "Ana", True], [2, None, False]]),
        Table(name="mala", columns=[Column("id", "INTEGER"), Column("id", "TEXT")], rows=[[1, "x"]]),
    ]


@salta_sin_pg
def test_pe01_ciclo_vida(tmp_path):
    """PE-01: arranca, crea BD de sesión y cierra sin residuos."""
    import psycopg
    eng = PGEngine(base_dir=str(tmp_path))
    try:
        assert eng.connected
        assert eng.dbname.startswith("sqllab_")
        with psycopg.connect(eng.dsn(), autocommit=True) as c:
            assert c.execute("SELECT 1").fetchone() == (1,)
    finally:
        eng.close()
    assert not eng.connected


@salta_sin_pg
def test_pe02_execute_paridad(tmp_path):
    """PE-02: simple + multi-sentencia (último con filas) + error amable."""
    eng = PGEngine(base_dir=str(tmp_path))
    try:
        eng.load_tables(_tablas_demo()[:1])
        r = eng.execute("SELECT nombre FROM clientes WHERE id = 1")
        assert r.ok and r.columns == ["nombre"] and r.rows == [["Ana"]]
        r = eng.execute("SELECT 1; SELECT nombre FROM clientes WHERE vip = TRUE;")
        assert r.ok and r.rows == [["Ana"]]
        r = eng.execute("SELECT * FROM noexiste")
        assert not r.ok and r.error
        r = eng.execute("   ")
        assert r.ok
    finally:
        eng.close()


@salta_sin_pg
def test_pe03_dialecto_nativo(tmp_path):
    """PE-03: date_part, ::, USING, ILIKE, RETURNING sin reescritura."""
    eng = PGEngine(base_dir=str(tmp_path))
    try:
        eng.load_tables(_tablas_demo()[:1])
        r = eng.execute("SELECT date_part('year', DATE '2024-05-01')")
        assert r.ok and r.rows == [[2024.0]]
        r = eng.execute("SELECT '5'::INTEGER + 1")
        assert r.ok and r.rows == [[6]]
        r = eng.execute("SELECT a.id FROM clientes a JOIN clientes b USING (id) LIMIT 1")
        assert r.ok and r.rows == [[1]]
        r = eng.execute("SELECT 'Ana' ILIKE 'ana'")
        assert r.ok and r.rows == [[True]]
        r = eng.execute("INSERT INTO clientes VALUES (9, 'Zed', FALSE) RETURNING id")
        assert r.ok
    finally:
        eng.close()


def test_pe04_tipos_con_sufijo():
    """Regresión: 'INTEGER PRIMARY KEY' conserva INTEGER (no TEXT)."""
    from core.pg_engine import _tipo_pg
    assert _tipo_pg("INTEGER PRIMARY KEY") == "INTEGER PRIMARY KEY"
    assert _tipo_pg("VARCHAR(10)") == "VARCHAR(10)"
    assert _tipo_pg("DOUBLE PRECISION") == "DOUBLE PRECISION"
    assert _tipo_pg("COSA") == "TEXT"
    assert _tipo_pg("") == "TEXT"


@salta_sin_pg
def test_pe04_load_paridad_y_omitidas(tmp_path):
    """PE-04: tipos, truncado/relleno, tabla inválida omitida."""
    eng = PGEngine(base_dir=str(tmp_path))
    try:
        omitidas = eng.load_tables(_tablas_demo())
        assert omitidas == ["mala"]
        assert eng.table_names() == ["clientes"]
        assert eng.column_names("clientes") == ["id", "nombre", "vip"]
        r = eng.execute("SELECT vip FROM clientes ORDER BY id")
        assert r.ok and r.rows == [[True], [False]]
    finally:
        eng.close()


@salta_sin_pg
def test_pe05_exportar_db(tmp_path):
    """PE-05: dump restorable con los datos."""
    eng = PGEngine(base_dir=str(tmp_path))
    try:
        eng.load_tables(_tablas_demo()[:1])
        dest = str(tmp_path / "out.sql")
        eng.exportar_db(dest)
        assert os.path.getsize(dest) > 0
        with open(dest, encoding="utf-8", errors="replace") as fh:
            txt = fh.read()
        assert "clientes" in txt and "Ana" in txt
    finally:
        eng.close()
        shutil.rmtree(str(tmp_path / "sqllab-pgdata-17"), ignore_errors=True)


@salta_sin_pg
def test_pe06_adopcion_servidor_ajeno(tmp_path):
    """Dos servidores sobre el mismo template: el 2º adopta (sin lock)."""
    from core.pg_engine import PGEngine, PGServer
    srv1 = PGServer(base_dir=str(tmp_path))
    srv1.start()
    try:
        srv2 = PGServer(base_dir=str(tmp_path))
        srv2.start()
        assert srv2.adoptado and srv2.puerto == srv1.puerto
        e1 = PGEngine(server=srv1, dbname="sqllab_ad1")
        e2 = PGEngine(server=srv2, dbname="sqllab_ad2")
        try:
            e1.load_tables(_tablas_demo()[:1])
            r = e2.execute("SELECT 1")
            assert r.ok
        finally:
            e1.close()
            e2.close()
        srv2.stop()  # adoptado: no-op, el servidor sigue vivo
        assert srv1.vivo
    finally:
        srv1.stop()
    assert not srv1.vivo
