from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import QHeaderView, QTableWidget, QTableWidgetItem

# Tenue oficial del tema oscuro (MutedLabel/StatusLabel en dark.qss).
NULL_TENUE = QColor("#4d7c6d")


def _configurar_grilla_ancha(grilla: QTableWidget) -> None:
    """Columnas legibles con scroll horizontal (spec visor-tablas-anchas).

    Reemplaza el Stretch global: cada sección se ajusta a su contenido
    (tope 300 px, elipsis), la última absorbe el hueco sobrante y cada
    celda lleva tooltip con el valor completo.
    """
    header = grilla.horizontalHeader()
    header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
    header.setMaximumSectionSize(300)
    header.setStretchLastSection(True)
    grilla.setTextElideMode(Qt.TextElideMode.ElideRight)
    grilla.setWordWrap(False)


def _ajustar_anchos(
    grilla: QTableWidget, headers: list[str], rows: list[list], muestra_medicion: int
) -> None:
    """Anchos por muestreo (primeras MUESTRA_MEDICION filas + cabecera).

    Evita medir todas las celdas en tablas grandes; tope 300 px.
    El usuario puede reajustar a mano (modo Interactive).
    """
    fm = grilla.fontMetrics()
    for c, h in enumerate(headers):
        w = fm.horizontalAdvance(h) + 20
        for row in rows[:muestra_medicion]:
            if c < len(row) and row[c] is not None:
                w = max(w, fm.horizontalAdvance(str(row[c])) + 20)
            elif c < len(row) and row[c] is None:
                w = max(w, fm.horizontalAdvance("NULL") + 20)
        grilla.setColumnWidth(c, min(w, 300))


def _item_grilla(value) -> QTableWidgetItem:
    """Celda de grilla: None se muestra como NULL tenue en cursiva (spec mostrar-null-en-grillas).

    "" sigue vacío; int/float a la derecha; el resto tal cual con tooltip.
    """
    if value is None:
        item = QTableWidgetItem("NULL")
        item.setToolTip("NULL")
        item.setForeground(NULL_TENUE)
        fuente = QFont(item.font())
        fuente.setItalic(True)
        item.setFont(fuente)
        return item
    texto = str(value)
    item = QTableWidgetItem(texto)
    if texto:
        item.setToolTip(texto)
    if isinstance(value, (int, float)):
        item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
    return item
