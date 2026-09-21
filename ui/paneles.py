"""Builders de paneles: HUD, banner, pista y matriz de esquema.

Mixin extraído de MainWindow (split Fase 2). Los builders crean los
widgets y los guardan como atributos; la lógica que los usa sigue en
MainWindow y se resuelve vía MRO.
"""
from __future__ import annotations

import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QToolButton,
    QVBoxLayout,
)


def _ruta_logo() -> str:
    """Ruta absoluta al logo SVG (válida en desarrollo y en build PyInstaller)."""
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources", "logo_sqllab.svg")


class PanelesMixin:
    def _build_hud(self) -> QFrame:
        bar = QFrame()
        bar.setObjectName("TitleBar")
        bar.setFixedHeight(40)
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(10, 0, 10, 0)
        lay.setSpacing(8)

        mark = QLabel()
        mark.setPixmap(QIcon(_ruta_logo()).pixmap(26, 26))
        mark.setToolTip("SQLab — práctica SQL 100 % local y sin conexión")
        lay.addWidget(mark)

        tag = QLabel("SQLab")
        tag.setObjectName("SysTag")
        tag.setToolTip("SQLab — práctica SQL 100 % local y sin conexión")
        lay.addWidget(tag)
        lay.addStretch()

        self.btn_json = QPushButton("PLANTILLA JSON PARA IA")
        self.btn_json.setObjectName("GhostBtn")
        self.btn_json.setToolTip("Ver la plantilla JSON para pedir ejercicios nuevos a IA")
        self.btn_cargar = QPushButton("CARGAR")
        self.btn_cargar.setObjectName("PrimaryBtn")
        self.btn_cargar.setToolTip(
            "Cargar una base para trabajar: EJERCICIO (.json), TABLAS desde "
            "ARCHIVOS (*.csv, *.xlsx, *.xls, *.db, multi-selección) o desde "
            "una CARPETA. UTF-8/BOM, delimitador , o ; auto, solo 1ª hoja "
            "en Excel, .db en solo lectura. Ext. insensible a mayúsculas."
        )
        self.btn_save = QPushButton("GUARDAR SESIÓN")
        self.btn_save.setObjectName("GhostBtn")
        self.btn_save.setToolTip("Guardar la sesión actual (tablas + ejercicio + historial)")
        self.btn_guardar = self.btn_save  # compat
        self.btn_exportar_db = QPushButton("EXPORTAR DB")
        self.btn_exportar_db.setObjectName("GhostBtn")
        self.btn_exportar_db.setToolTip("Guardar la base en memoria en un fichero .db real")
        self.btn_ses = QPushButton("CARGAR SESIÓN")
        self.btn_ses.setObjectName("GhostBtn")
        self.btn_ses.setToolTip("Cargar una sesión guardada anteriormente")
        self.btn_cargar_sesion = self.btn_ses  # compat
        for b in (self.btn_json, self.btn_cargar, self.btn_save, self.btn_exportar_db, self.btn_ses):
            lay.addWidget(b)
        lay.addWidget(self._build_crono())
        return bar

    def _sep(self) -> QLabel:
        s = QLabel("|")
        s.setObjectName("MutedLabel")
        return s

    def _build_banner(self) -> QFrame:
        banner = QFrame()
        banner.setObjectName("ExerciseBanner")
        banner.setFixedHeight(38)
        lay = QHBoxLayout(banner)
        lay.setContentsMargins(10, 0, 10, 0)
        lay.setSpacing(8)

        lvl = QLabel("[NIVEL]:")
        lvl.setObjectName("MutedLabel")
        lay.addWidget(lvl)
        self.difficulty_badge = QLabel("PRINCIPIANTE")
        self.difficulty_badge.setObjectName("LevelBadge")
        lay.addWidget(self.difficulty_badge)
        lay.addWidget(self._sep())
        mtag = QLabel("[MISIÓN]:")
        mtag.setObjectName("MissionTag")
        lay.addWidget(mtag)
        self.exercise_title = QLabel("SIN EJERCICIO")
        self.exercise_title.setObjectName("ExerciseTitle")
        lay.addWidget(self.exercise_title, stretch=1)
        self.enunciado_titulo = self.exercise_title  # compat

        self.pista_toggle = QToolButton()
        self.pista_toggle.setObjectName("PistaToggle")
        self.pista_toggle.setText("VER_PISTA")
        self.pista_toggle.setCheckable(True)
        self.pista_toggle.setChecked(False)
        self.pista_toggle.setToolTip("Mostrar u ocultar la pista del ejercicio")
        lay.addWidget(self.pista_toggle)
        self.btn_preset_tienda = QPushButton("EJEMPLO: TIENDA")
        self.btn_preset_tienda.setObjectName("GhostBtn")
        self.btn_preset_tienda.setToolTip("Cargar el ejercicio de ejemplo de la tienda")
        self.btn_preset_biblio = QPushButton("EJEMPLO: BIBLIOTECA")
        self.btn_preset_biblio.setObjectName("GhostBtn")
        self.btn_preset_biblio.setToolTip("Cargar el ejercicio de ejemplo de la biblioteca")
        lay.addWidget(self.btn_preset_tienda)
        lay.addWidget(self.btn_preset_biblio)
        return banner

    def _build_hint_drawer(self) -> QFrame:
        drawer = QFrame()
        drawer.setObjectName("HintDrawer")
        lay = QHBoxLayout(drawer)
        lay.setContentsMargins(12, 5, 12, 5)
        lay.setSpacing(8)
        tag = QLabel("PISTA:")
        tag.setObjectName("HintTag")
        lay.addWidget(tag)
        self.pista_label = QLabel("")
        self.pista_label.setObjectName("HintText")
        self.pista_label.setWordWrap(True)
        lay.addWidget(self.pista_label, stretch=1)
        close_btn = QPushButton("[CERRAR]")
        close_btn.setObjectName("GhostBtn")
        close_btn.clicked.connect(lambda: self.pista_toggle.setChecked(False))
        lay.addWidget(close_btn)
        drawer.setVisible(False)
        self.pista_card = drawer  # compat
        return drawer

    # ---------------------------------------------------------- left matrix

    def _build_matrix(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("LeftPanel")
        panel.setMinimumWidth(260)
        panel.setMaximumWidth(300)
        lay = QVBoxLayout(panel)
        lay.setContentsMargins(8, 8, 8, 8)
        lay.setSpacing(6)

        head = QHBoxLayout()
        head.setContentsMargins(0, 0, 0, 0)
        t = QLabel("> ESQUEMA DE TABLAS")
        t.setObjectName("PanelTitle")
        head.addWidget(t)
        self.tables_count = QLabel("(0)")
        self.tables_count.setObjectName("PanelTitle")
        head.addWidget(self.tables_count)
        head.addStretch()
        self.btn_reset = QPushButton("⟳")
        self.btn_reset.setObjectName("GhostBtn")
        self.btn_reset.setFixedWidth(28)
        self.btn_reset.setToolTip("Restablecer tablas originales")
        head.addWidget(self.btn_reset)
        lay.addLayout(head)

        self.tabla_list = QListWidget()
        self.tabla_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tabla_list.setMaximumHeight(130)
        self.tabla_list.setToolTip("Tablas cargadas: selecciona una para ver sus columnas y datos")
        lay.addWidget(self.tabla_list)

        node_head = QHBoxLayout()
        node_head.setContentsMargins(0, 0, 0, 0)
        node_lab = QLabel("TABLA ACTIVA:")
        node_lab.setObjectName("MutedLabel")
        node_head.addWidget(node_lab)
        self.schema_label = QLabel("")
        self.schema_label.setObjectName("NodeName")
        node_head.addWidget(self.schema_label, stretch=1)
        colmap = QLabel("COLUMNAS")
        colmap.setObjectName("MutedLabel")
        node_head.addWidget(colmap)
        lay.addLayout(node_head)
        self.columnas_title = QLabel("")  # compat
        self.columnas_title.setVisible(False)
        self.columnas_list = QListWidget()
        self.columnas_list.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.columnas_list.setToolTip("Clic en una columna para insertarla en el editor")
        lay.addWidget(self.columnas_list, stretch=1)
        self.columnas_empty = QLabel("Selecciona un nodo para ver su mapa de columnas.")
        self.columnas_empty.setObjectName("MutedLabel")
        self.columnas_empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.columnas_empty.setWordWrap(True)
        self.columnas_label = self.columnas_empty  # compat
        lay.addWidget(self.columnas_empty, stretch=1)

        self.btn_select_all = QPushButton("> INSERTAR `SELECT *` EN EL EDITOR")
        self.btn_select_all.setObjectName("GhostBtn")
        self.btn_select_all.setToolTip("Escribe SELECT * de la tabla activa y lo ejecuta")
        lay.addWidget(self.btn_select_all)

        log_head = QHBoxLayout()
        log_head.setContentsMargins(0, 0, 0, 0)
        lt = QLabel("> HISTORIAL DE CONSULTAS")
        lt.setObjectName("PanelTitle")
        log_head.addWidget(lt)
        log_head.addStretch()
        self.historial_toggle = QToolButton()
        self.historial_toggle.setObjectName("PistaToggle")
        self.historial_toggle.setText("VER_HISTORIAL")
        self.historial_toggle.setCheckable(True)
        self.historial_toggle.setChecked(False)
        self.historial_toggle.setToolTip("Mostrar u ocultar el historial de consultas")
        log_head.addWidget(self.historial_toggle)
        self.btn_clear_hist = QPushButton("[LIMPIAR]")
        self.btn_clear_hist.setObjectName("GhostBtn")
        log_head.addWidget(self.btn_clear_hist)
        lay.addLayout(log_head)
        self.historial_list = QListWidget()
        self.historial_list.setObjectName("HistorialList")
        self.historial_list.setMaximumHeight(120)
        self.historial_list.setToolTip("Clic en una consulta para recargarla y ejecutarla")
        self.historial_list.setVisible(False)
        lay.addWidget(self.historial_list)

        tx = QHBoxLayout()
        tx.setContentsMargins(0, 0, 0, 0)
        self.status_db = QLabel("TABLAS: 0 · FILAS: 0 · DB: MEMORIA OK")
        self.status_db.setObjectName("StatusLabel")
        tx.addWidget(self.status_db)
        tx.addStretch()
        lay.addLayout(tx)
        return panel
