"""Spec abrir-db-existente — cargar ficheros .db/.sqlite como sesión."""
from __future__ import annotations

import sqlite3


def _make_db(path, with_empty: bool = True):
    con = sqlite3.connect(str(path))
    con.execute('CREATE TABLE clientes (id INTEGER, nombre TEXT, nota TEXT)')
    con.execute("INSERT INTO clientes VALUES (1, 'Ana', NULL)")
    con.execute("INSERT INTO clientes VALUES (2, 'NA', '-')")
    con.execute('CREATE TABLE pedidos (id INTEGER, total REAL)')
    con.execute("INSERT INTO pedidos VALUES (1, 10.5)")
    if with_empty:
        con.execute('CREATE TABLE vacia (id INTEGER)')
    con.commit()
    con.close()


def test_db01_tablas_datos_y_nulos(tmp_path):
    """DB-01: tablas de usuario, tipos, filas y None intactos."""
    from core.session_loader import load_file

    p = tmp_path / "datos.db"
    _make_db(p)
    res = load_file(str(p))
    assert res.ok, res.errors
    names = {t.name for t in res.tables}
    assert names == {"clientes", "pedidos", "vacia"}
    cli = next(t for t in res.tables if t.name == "clientes")
    assert [c.name for c in cli.columns] == ["id", "nombre", "nota"]
    assert cli.rows[0] == [1, "Ana", None]
    # dato explícito: NO se aplica el set de nulos (como JSON)
    assert cli.rows[1] == [2, "NA", "-"]
    assert next(t for t in res.tables if t.name == "vacia").rows == []


def test_db01_sqlite3_ext(tmp_path):
    """DB-01: extensión .sqlite3 aceptada."""
    from core.session_loader import load_file

    p = tmp_path / "d.sqlite3"
    _make_db(p, with_empty=False)
    res = load_file(str(p))
    assert res.ok, res.errors
    assert {t.name for t in res.tables} == {"clientes", "pedidos"}


def test_db01_e2e_select(tmp_path):
    """DB-01 E2E: lo cargado se consulta vía engine."""
    from core.session_loader import load_file
    from core.sqlite_engine import SQLEngine

    p = tmp_path / "q.db"
    _make_db(p, with_empty=False)
    res = load_file(str(p))
    eng = SQLEngine()
    assert eng.load_tables(res.tables) == []
    r = eng.execute("SELECT nombre FROM clientes WHERE nota IS NULL")
    assert r.ok and r.rows == [["Ana"]]


def test_db03_corrupto_y_sin_tablas(tmp_path):
    """DB-03: corrupto o sin tablas → error español, sin crash."""
    from core.session_loader import load_file

    malo = tmp_path / "malo.db"
    malo.write_bytes(b"esto no es sqlite")
    res = load_file(str(malo))
    assert not res.ok and res.errors
    vacio = tmp_path / "vacio.db"
    sqlite3.connect(str(vacio)).close()
    res2 = load_file(str(vacio))
    assert not res2.ok and res2.errors


def test_db04_solo_lectura(tmp_path):
    """DB-04: el fichero no se modifica al cargar."""
    from core.session_loader import load_file

    p = tmp_path / "ro.db"
    _make_db(p, with_empty=False)
    antes = p.read_bytes()
    res = load_file(str(p))
    assert res.ok, res.errors
    assert p.read_bytes() == antes
    assert list(tmp_path.glob("ro.db-*")) == []
