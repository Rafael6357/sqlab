from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import QHeaderView, QTableWidget, QTableWidgetItem

# Tenue oficial del tema oscuro (MutedLabel/StatusLabel en dark.qss).
NULL_TENUE = QColor("#4d7c6d")


def _configurar_grilla_ancha(grilla: QTableWidget) -> None:
    """Columnas legibles con scroll horizontal (spec visor-tablas-anchas).

    Secciones interactivas con elipsis; el tope de 300 px vive en la
    MEDICIÓN (`_ajustar_anchos`), no en el header: así `repartir_...`
    puede rellenar proporcionalmente en tablas angostas (spec auto-espaciado).
    """
    header = grilla.horizontalHeader()
    header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
    header.setStretchLastSection(False)
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


def guardar_base_anchos(grilla: QTableWidget) -> None:
    """Guarda los anchos actuales como base del reparto proporcional."""
    header = grilla.horizontalHeader()
    grilla.setProperty("anchos_base", [header.sectionSize(i) for i in range(grilla.columnCount())])


def repartir_anchos_proporcional(grilla: QTableWidget) -> None:
    """Reparte el hueco sobrante entre columnas en proporción a su base (AE-02/AE-03).

    Sin hueco (total >= viewport) no toca nada. O(columnas), sin recorrer celdas.
    """
    base = grilla.property("anchos_base")
    if not base:
        guardar_base_anchos(grilla)
        base = grilla.property("anchos_base")
    if not base:
        return
    total = sum(base)
    vp = grilla.viewport().width()
    if vp <= 0 or vp <= total:
        return
    extra = vp - total
    header = grilla.horizontalHeader()
    signals = header.blockSignals(True)
    try:
        for i, b in enumerate(base):
            header.resizeSection(i, max(1, b + round(extra * b / total)))
    finally:
        header.blockSignals(signals)
    guardar_base_anchos(grilla)


def ajustar_y_repartir(
    grilla: QTableWidget, headers: list[str], rows: list[list], muestra_medicion: int
) -> None:
    """Mide por muestreo, guarda la base y rellena proporcional (AE-01..AE-03)."""
    _ajustar_anchos(grilla, headers, rows, muestra_medicion)
    guardar_base_anchos(grilla)
    repartir_anchos_proporcional(grilla)
