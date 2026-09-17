"""Spec visor-tablas-anchas — tablas anchas legibles con scroll horizontal."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QHeaderView


def _tabla_ancha():
    """Fixture sintético: 60 columnas × 5 filas (sin datos reales)."""
    from core.sqlite_engine import Column, Table
    cols = [Column(name=f"columna_{i:02d}", type="TEXT") for i in range(60)]
    rows = [[f"valor_fila{r}_columna_{c:02d}_texto_largo" for c in range(60)] for r in range(5)]
    return Table(name="ancha", columns=cols, rows=rows)


def _mostrar_visor(app, qtbot):
    app._refresh_dump(_tabla_ancha())
    qtbot.wait(50)
    QApplication.processEvents()
    return app.visor_tabla


def test_va01_visor_sin_stretch_con_scroll(app, qtbot):
    """VA-01: header no-Stretch y ancho total > viewport (scroll real)."""
    visor = _mostrar_visor(app, qtbot)
    assert visor.horizontalHeader().sectionResizeMode(0) != QHeaderView.ResizeMode.Stretch
    total = sum(visor.horizontalHeader().sectionSize(i) for i in range(visor.columnCount()))
    assert total > visor.viewport().width(), f"sin scroll: total={total}"


def test_va01_resultado_sin_stretch_con_scroll(app, qtbot):
    """VA-01 también en RESULTADO DE LA CONSULTA."""
    cols = [f"columna_{i:02d}" for i in range(60)]
    rows = [[f"v{r}_{c}" for c in range(60)] for r in range(5)]
    app._mostrar_resultado(cols, rows)
    qtbot.wait(50)
    QApplication.processEvents()
    res = app.resultado_tabla
    assert res.horizontalHeader().sectionResizeMode(0) != QHeaderView.ResizeMode.Stretch
    total = sum(res.horizontalHeader().sectionSize(i) for i in range(res.columnCount()))
    assert total > res.viewport().width(), f"sin scroll: total={total}"


def test_va02_tooltip_con_valor_completo(app, qtbot):
    """VA-02: cada celda lleva tooltip con el texto íntegro."""
    visor = _mostrar_visor(app, qtbot)
    item = visor.item(0, 0)
    assert item.toolTip() == "valor_fila0_columna_00_texto_largo"
    cols = ["a", "b"]
    app._mostrar_resultado(cols, [["corto", "texto_muy_largo_para_ver_el_tooltip"]])
    assert app.resultado_tabla.item(0, 1).toolTip() == "texto_muy_largo_para_ver_el_tooltip"


def test_va03_ultima_columna_absorbe_hueco(app):
    """VA-03: tablas angostas sin huecos raros a la derecha."""
    assert app.visor_tabla.horizontalHeader().stretchLastSection()
    assert app.resultado_tabla.horizontalHeader().stretchLastSection()


def test_va04_tope_ancho_y_elipsis(app, qtbot):
    """VA-04: secciones topadas a 300px con elipsis."""
    visor = _mostrar_visor(app, qtbot)
    assert visor.horizontalHeader().maximumSectionSize() == 300
    assert visor.textElideMode() == Qt.TextElideMode.ElideRight
    assert app.resultado_tabla.textElideMode() == Qt.TextElideMode.ElideRight
    anchos = [visor.horizontalHeader().sectionSize(i) for i in range(visor.columnCount())]
    assert all(a <= 300 for a in anchos), f"sección sin tope: {max(anchos)}"


def test_va05_headers_intactos(app, qtbot):
    """VA-05: cabeceras col ::tipo del visor intactas con tabla ancha."""
    visor = _mostrar_visor(app, qtbot)
    assert visor.columnCount() == 60
    assert visor.horizontalHeaderItem(0).text() == "columna_00 ::TEXT"
    assert visor.rowCount() == 5
