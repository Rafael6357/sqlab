"""Gráficos básicos del resultado (spec graficos-basicos).

`datos_para_grafico` es lógica pura (testeable sin Qt Charts); `DialogoGrafico`
dibuja barras/líneas con PySide6.QtCharts en tema oscuro + exporta PNG.
"""
from __future__ import annotations

MAX_PUNTOS = 200


def datos_para_grafico(columns: list[str], rows: list[list]) -> tuple[list[str], list[float]] | None:
    """Mapea resultado de 2 columnas (etiqueta, valor) a puntos.

    Devuelve (etiquetas, valores) o None si no graficable. Salta filas con
    valor None/no-numérico; topa en MAX_PUNTOS.
    """
    if len(columns) != 2 or not rows:
        return None
    etiquetas: list[str] = []
    valores: list[float] = []
    for row in rows[:MAX_PUNTOS]:
        if len(row) < 2:
            continue
        try:
            v = float(row[1]) if row[1] is not None else None
        except (TypeError, ValueError):
            continue
        if v is None:
            continue
        etiquetas.append("" if row[0] is None else str(row[0]))
        valores.append(v)
    if not valores:
        return None
    return etiquetas, valores


def puede_graficar(columns: list[str], rows: list[list]) -> bool:
    """True si hay al menos 1 punto graficable."""
    return datos_para_grafico(columns, rows) is not None


try:
    from PySide6.QtCharts import (
        QBarCategoryAxis,
        QBarSeries,
        QBarSet,
        QChart,
        QChartView,
        QLineSeries,
        QValueAxis,
    )
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QColor, QPainter
    from PySide6.QtWidgets import (
        QComboBox,
        QDialog,
        QFileDialog,
        QHBoxLayout,
        QPushButton,
        QVBoxLayout,
    )

    _QTCHARTS = True
except ImportError:  # pragma: no cover - entorno sin PySide6-Addons
    _QTCHARTS = False


if _QTCHARTS:

    class DialogoGrafico(QDialog):
        """Diálogo con gráfico de barras/líneas + GUARDAR PNG (GR-01/GR-03)."""

        FONDO = "#0a1212"
        SERIE = "#00ffaa"
        TEXTO = "#d7ffec"

        def __init__(self, parent, titulo: str, etiquetas: list[str], valores: list[float]) -> None:
            super().__init__(parent)
            self.setWindowTitle(titulo)
            self.resize(640, 420)
            self.setModal(True)
            lay = QVBoxLayout(self)
            fila = QHBoxLayout()
            self.combo = QComboBox()
            self.combo.addItems(["BARRAS", "LÍNEAS"])
            self.combo.currentIndexChanged.connect(self._repintar)
            fila.addWidget(self.combo)
            fila.addStretch()
            btn_png = QPushButton("GUARDAR PNG")
            btn_png.setObjectName("GhostBtn")
            btn_png.clicked.connect(self.guardar_png)
            fila.addWidget(btn_png)
            lay.addLayout(fila)
            self.vista = QChartView()
            self.vista.setRenderHint(QPainter.RenderHint.Antialiasing)
            lay.addWidget(self.vista)
            self._etiquetas = etiquetas
            self._valores = valores
            self._repintar()

        def _repintar(self) -> None:
            chart = QChart()
            chart.setBackgroundVisible(True)
            chart.setTheme(QChart.ChartTheme.ChartThemeDark)
            chart.setBackgroundBrush(QColor(self.FONDO))
            if self.combo.currentText() == "LÍNEAS":
                serie = QLineSeries()
                for i, v in enumerate(self._valores):
                    serie.append(i, v)
                serie.setColor(QColor(self.SERIE))
                chart.addSeries(serie)
                chart.createDefaultAxes()
            else:
                bset = QBarSet("")
                bset.setColor(QColor(self.SERIE))
                for v in self._valores:
                    bset.append(v)
                serie = QBarSeries()
                serie.append(bset)
                chart.addSeries(serie)
                cats = QBarCategoryAxis()
                cats.append(self._etiquetas)
                cats.setLabelsColor(QColor(self.TEXTO))
                chart.addAxis(cats, Qt.AlignmentFlag.AlignBottom)
                serie.attachAxis(cats)
                eje_y = QValueAxis()
                eje_y.setLabelsColor(QColor(self.TEXTO))
                chart.addAxis(eje_y, Qt.AlignmentFlag.AlignLeft)
                serie.attachAxis(eje_y)
            chart.legend().setVisible(False)
            self.vista.setChart(chart)

        def guardar_png(self) -> None:
            path, _ = QFileDialog.getSaveFileName(self, "GUARDAR GRÁFICO", "grafico.png", "PNG (*.png)")
            if not path:
                return
            self.vista.grab().save(path)
