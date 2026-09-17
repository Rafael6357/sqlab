"""Spec formato-sql-real — formateo con cláusulas, indentación y protección."""
from __future__ import annotations


def _fmt(sql: str) -> str:
    from ui.main_window import _formatear_sql
    return _formatear_sql(sql)


def test_fs01_clausulas_basicas():
    """FS-01: salto antes de cada cláusula principal."""
    out = _fmt("select a, b from t where x=1 order by a")
    assert out == "SELECT a, b\nFROM t\nWHERE x = 1\nORDER BY a"


def test_fs01_group_having_limit():
    out = _fmt("select d, count(*) from t group by d having count(*) > 1 limit 10")
    assert out == (
        "SELECT d, COUNT(*)\nFROM t\nGROUP BY d\nHAVING COUNT(*) > 1\nLIMIT 10"
    )


def test_fs02_subconsulta_indentada():
    """FS-02: interior de subconsulta con un nivel extra."""
    out = _fmt("select * from (select id from t where n>0) as s")
    assert out == "SELECT *\nFROM (\n  SELECT id\n  FROM t\n  WHERE n > 0\n) AS s"


def test_fs03_literal_simple_intacto():
    """FS-03: literales no se tocan."""
    out = _fmt("select * from clientes where nombre = 'from spain'")
    assert "'from spain'" in out
    assert "WHERE nombre = 'from spain'" in out


def test_fs03_literal_escapado_y_doble_comilla():
    out = _fmt('select "from" from t where a = \'it\'\'s\'')
    assert '"from"' in out
    assert "'it''s'" in out
    assert out.startswith("SELECT")


def test_fs03_comentarios_intactos():
    out = _fmt("select * from t -- select secreto")
    assert "-- select secreto" in out
    assert "-- SELECT" not in out
    out2 = _fmt("select * from t /* where x from y */")
    assert "/* where x from y */" in out2
    assert "/* WHERE" not in out2


def test_fs04_idempotente():
    """FS-04: formatear dos veces da lo mismo."""
    once = _fmt("select a from t where x=1 and y=2 order by a")
    assert _fmt(once) == once


def test_fs06_join_y_and_or():
    """FS-06: JOINs en líneas propias, AND/OR indentados."""
    out = _fmt("select a from t1 join t2 on t1.id=t2.id where a>1 and b<2 or c=3")
    assert out == (
        "SELECT a\nFROM t1\nJOIN t2\n  ON t1.id = t2.id\nWHERE a > 1\n  AND b < 2\n  OR c = 3"
    )


def test_fs_vacio():
    assert _fmt("") == ""
    assert _fmt("   \n  ") == ""


def test_fs_no_rompe_palabras_con_keywords():
    """selección / fromage no se tocan."""
    out = _fmt("select selección, fromage from t")
    assert "selección" in out and "fromage" in out


def test_fs_multiples_sentencias():
    out = _fmt("select 1; select 2;")
    assert out == "SELECT 1;\nSELECT 2;"


def test_ui_boton_formato_no_checkable_aplica(app):
    """FS-05: botón normal que aplica el formato al editor."""
    assert not app.btn_format.isCheckable()
    assert app.btn_format.text() == "FORMATO SQL"
    app.editor.setPlainText("select a from t where x=1")
    app.formatear_consulta()
    assert app.editor.toPlainText() == "SELECT a\nFROM t\nWHERE x = 1"
    assert "FORMATEADA" in app.exec_time.text()
