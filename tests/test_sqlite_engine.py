"""Tests unitarios de core/sqlite_engine.py — sin dependencia Qt."""
from core.sqlite_engine import SQLEngine, Column, Table


def _sample_tables():
    clientes = Table(
        name="clientes",
        columns=[
            Column(name="id", type="INTEGER PRIMARY KEY"),
            Column(name="nombre", type="TEXT"),
            Column(name="ciudad", type="TEXT"),
        ],
        rows=[
            [1, "Ana", "Montevideo"],
            [2, "Bruno", "Buenos Aires"],
        ],
    )
    return [clientes]


def test_engine_init_not_connected():
    e = SQLEngine()
    assert not e.connected
    assert e.tables == {}


def test_load_tables_and_connect():
    e = SQLEngine()
    e.load_tables(_sample_tables())
    assert e.connected
    assert "clientes" in e.table_names()
    assert len(e.tables["clientes"].rows) == 2


def test_execute_select_star():
    e = SQLEngine()
    e.load_tables(_sample_tables())
    r = e.execute("SELECT * FROM clientes;")
    assert r.ok
    assert len(r.rows) == 2
    assert r.columns == ["id", "nombre", "ciudad"]


def test_execute_select_where():
    e = SQLEngine()
    e.load_tables(_sample_tables())
    r = e.execute("SELECT nombre FROM clientes WHERE id = 1")
    assert r.ok
    assert r.rows == [["Ana"]]


def test_execute_no_tables():
    e = SQLEngine()
    r = e.execute("SELECT 1")
    assert not r.ok
    assert "tablas" in r.error.lower() or "carga" in r.error.lower()


def test_execute_syntax_error():
    e = SQLEngine()
    e.load_tables(_sample_tables())
    r = e.execute("SELEC * FROM clientes")
    assert not r.ok
    assert r.error  # error traducido por friendly_error


def test_execute_empty_query():
    e = SQLEngine()
    e.load_tables(_sample_tables())
    r = e.execute("")
    assert r.ok
    assert r.message


def test_execute_insert():
    e = SQLEngine()
    e.load_tables(_sample_tables())
    r = e.execute("INSERT INTO clientes VALUES (3, 'Carla', 'Lima')")
    assert r.ok
    r2 = e.execute("SELECT COUNT(*) FROM clientes")
    assert r2.rows[0][0] == 3


def test_execute_create_table():
    e = SQLEngine()
    e.load_tables(_sample_tables())
    r = e.execute("CREATE TABLE test (id INTEGER, val TEXT)")
    assert r.ok
    # CREATE TABLE crea en la conexión pero no se refleja en self.tables
    r2 = e.execute("INSERT INTO test VALUES (1, 'ok')")
    assert r2.ok
    r3 = e.execute("SELECT * FROM test")
    assert r3.ok and r3.rows == [[1, "ok"]]


def test_table_names_and_column_names():
    e = SQLEngine()
    e.load_tables(_sample_tables())
    assert e.table_names() == ["clientes"]
    assert e.column_names("clientes") == ["id", "nombre", "ciudad"]
    assert e.column_names("noexiste") == []


def test_close_disconnects():
    e = SQLEngine()
    e.load_tables(_sample_tables())
    assert e.connected
    e.close()
    assert not e.connected
    assert e.table_names() == []  # IA-01 / SC-10


def test_close_double():
    """close() dos veces no debe lanzar y sigue limpio."""
    e = SQLEngine()
    e.load_tables(_sample_tables())
    e.close()
    e.close()
    assert not e.connected
    assert e.table_names() == []


def test_close_sin_conexion():
    """Motor recién creado: close() es no-op y table_names() vacío."""
    e = SQLEngine()
    e.close()
    assert not e.connected
    assert e.table_names() == []


def test_load_tables_empty():
    e = SQLEngine()
    e.load_tables([])
    assert not e.connected
    assert e.tables == {}


def test_load_tables_fila_larga_se_trunca():
    e = SQLEngine()
    t = Table(name="t1", columns=[Column("a", "INTEGER"), Column("b", "INTEGER")], rows=[[1, 2, 3]])
    e.load_tables([t])
    assert e.connected
    r = e.execute("SELECT * FROM t1")
    assert r.ok
    assert r.rows == [[1, 2]]


def test_load_tables_fila_corta_se_rellena():
    e = SQLEngine()
    t = Table(name="t2", columns=[Column("a", "INTEGER"), Column("b", "INTEGER"), Column("c", "INTEGER")], rows=[[1]])
    e.load_tables([t])
    assert e.connected
    r = e.execute("SELECT * FROM t2")
    assert r.ok
    assert r.rows == [[1, None, None]]


def test_load_tables_tabla_sin_columnas_se_ignora():
    e = SQLEngine()
    t = Table(name="t3", columns=[], rows=[[1]])
    e.load_tables([t])
    assert "t3" not in e.table_names()


def test_load_tables_columna_duplicada_se_ignora():
    e = SQLEngine()
    t = Table(name="t4", columns=[Column("id", "INTEGER"), Column("id", "TEXT")], rows=[[1, "x"]])
    e.load_tables([t])
    assert "t4" not in e.table_names()


def test_load_tables_celda_no_escalar_se_normaliza():
    e = SQLEngine()
    t = Table(name="t5", columns=[Column("a", "TEXT")], rows=[[["x", "y"]]])
    e.load_tables([t])
    assert e.connected
    r = e.execute("SELECT * FROM t5")
    assert r.ok
    assert len(r.rows) == 1


def test_load_tables_invalida_no_bloquea_a_validas():
    e = SQLEngine()
    mala = Table(name="mala", columns=[Column("id", "INTEGER"), Column("id", "TEXT")], rows=[[1, "x"]])
    buena = Table(name="buena", columns=[Column("a", "INTEGER")], rows=[[7]])
    e.load_tables([mala, buena])
    assert "mala" not in e.table_names()
    assert "buena" in e.table_names()
    r = e.execute("SELECT * FROM buena")
    assert r.ok
    assert r.rows == [[7]]
