"""Spec error-friendly-pg — errores PostgreSQL en español (FE)."""
from __future__ import annotations

import os

import pytest

from core.error_friendly import friendly_pg_error
from core.pg_engine import PG_BIN_DIR

REQUIERE_PG = not (PG_BIN_DIR and os.path.isfile(os.path.join(PG_BIN_DIR, "initdb.exe")))
salta_sin_pg = pytest.mark.skipif(REQUIERE_PG, reason="sin binarios PG vendoreados")


def _tablas_demo():
    from core.sqlite_engine import Column, Table
    return [
        Table(name="clientes", columns=[Column("id", "INTEGER"), Column("nombre", "TEXT")],
              rows=[[1, "Ana"]]),
    ]


def test_fe01_tabla_inexistente():
    """FE-01: 42P01 → español con nombre."""
    msg = friendly_pg_error('relation "pedidos" does not exist', sqlstate="42P01")
    assert "pedidos" in msg and "No existe la tabla" in msg


def test_fe01_columna_inexistente():
    """FE-01: 42703 → español con nombre."""
    msg = friendly_pg_error('column "monto" does not exist', sqlstate="42703")
    assert "monto" in msg and "No existe la columna" in msg


def test_fe02_sintaxis_y_funcion():
    """FE-02: 42601 con token; 42883 con hint de tipos (idents en minúsculas)."""
    msg = friendly_pg_error('syntax error at or near "SEL"', sqlstate="42601")
    assert "sel" in msg.lower() and "sintaxis" in msg.lower()
    msg = friendly_pg_error(
        "function date_part(unknown, integer) does not exist", sqlstate="42883"
    )
    assert "date_part" in msg
    # Español real de servidor con locale ES:
    msg = friendly_pg_error("no existe la columna «monto» de la relación «t»")
    assert "No existe la columna" in msg and "monto" in msg
    msg = friendly_pg_error("error de sintaxis cerca de «SELEKT»")
    assert "sintaxis" in msg.lower() and "selekt" in msg.lower()


def test_fe03_fallback_y_generico():
    """FE-03: sin sqlstate por texto; desconocido → genérico recortado."""
    msg = friendly_pg_error('relation "x" does not exist')
    assert "No existe la tabla" in msg
    msg = friendly_pg_error("FATAL: lo que sea " + "z" * 500)
    assert len(msg) <= 300 and "z" in msg


@salta_sin_pg
def test_fe04_e2e_sqlstate_real(tmp_path):
    """FE-04: error real del servidor llega traducido (sqlstate de psycopg)."""
    from core.pg_engine import PGEngine
    eng = PGEngine(base_dir=str(tmp_path))
    try:
        r = eng.execute("SELECT * FROM noexiste_xyz")
        assert not r.ok
        assert "noexiste_xyz" in r.error and "No existe la tabla" in r.error
        r = eng.execute("SELEKT 1")
        assert not r.ok and "sintaxis" in r.error.lower()
        eng.load_tables(_tablas_demo()[:1])
        r = eng.execute("SELECT nosuchcol FROM clientes")
        assert not r.ok and "No existe la columna" in r.error
    finally:
        eng.close()
