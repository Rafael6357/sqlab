"""Tests unitarios de core/error_friendly.py — sin dependencia Qt."""
from core.error_friendly import friendly_error


def test_no_such_table():
    msg = friendly_error('no such table: clientes', {'pedidos'})
    assert 'clientes' in msg.lower()
    assert 'no existe' in msg.lower() or 'No existe' in msg


def test_no_such_column():
    msg = friendly_error('no such column: telefono')
    assert 'telefono' in msg.lower() or 'teléfono' in msg.lower()


def test_syntax_error_near():
    msg = friendly_error('near "SELEC": syntax error')
    assert 'sintaxis' in msg.lower() or 'sintaxi' in msg.lower()


def test_syntax_error_general():
    msg = friendly_error('syntax error near ","')
    assert 'sintaxis' in msg.lower() or 'error' in msg.lower()


def test_incomplete_input():
    msg = friendly_error('incomplete input')
    assert 'incompleta' in msg.lower()


def test_no_such_function():
    msg = friendly_error('no such function: CONCAT')
    assert 'concat' in msg.lower()
    assert 'función' in msg.lower() or 'no existe' in msg.lower()


def test_ambiguous_column():
    msg = friendly_error('ambiguous column name: id')
    assert 'id' in msg


def test_constraint_failed():
    msg = friendly_error('constraint failed')
    assert 'restricción' in msg.lower() or 'violó' in msg.lower()


def test_foreign_key_failed():
    msg = friendly_error('foreign key constraint failed')
    assert 'llave' in msg.lower() or 'foránea' in msg.lower()


def test_datatype_mismatch():
    msg = friendly_error('datatype mismatch')
    assert 'tipo' in msg.lower() or 'datos' in msg.lower()


def test_unknown_error_fallback():
    msg = friendly_error('some really weird unknown sqlite error')
    assert 'error' in msg.lower()
    assert 'base de datos' in msg.lower()


def test_unknown_column_pattern():
    msg = friendly_error('unknown column xyz in field list')
    assert 'xyz' in msg


def test_table_has_no_column_named():
    msg = friendly_error('table clientes has no column named telefono')
    assert 'telefono' in msg.lower()
    assert 'columna' in msg.lower()


def test_table_has_no_such_column():
    msg = friendly_error('table pedidos has no such column total')
    assert 'total' in msg.lower() or 'columna' in msg.lower()
