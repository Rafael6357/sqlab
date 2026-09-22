"""Carga de datos: presets, ejercicio .json, tablas y aviso de tamaño.

Mixin extraído de MainWindow (split Fase 3). Solo toca atributos de carga
(`engine`, `ejercicio`, listas/etiquetas) y usa `_toast`, `_crono_reset`,
`_refresh_*` y `_limpiar_resultado` vía MRO.
"""
from __future__ import annotations

import os
import sys

from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from core.session_loader import (
    Ejercicio,
    combinar_resultados,
    load_file,
    load_tablas_folder,
)
from ui.dialogs import _show_custom_dialog


class CargaMixin:
    # ------------------------------------------------------------ carga

    def _base_dir(self) -> str:
        return os.path.dirname(os.path.abspath(__file__))

    @staticmethod
    def _bundle_dir() -> str:
        """Raíz del bundle: _MEIPASS en exe frozen, raíz del repo en dev.

        PyInstaller onefile extrae `datas` (resources/, examples/) a
        sys._MEIPASS; en dev los recursos viven junto al código.
        """
        if getattr(sys, "frozen", False):
            meipass = getattr(sys, "_MEIPASS", None)
            if meipass:
                return meipass
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def _load_initial_preset(self) -> None:
        # CV-01: al arrancar la consola queda vacía (sin defaultQuery inyectada)
        if not self.cargar_preset("ejemplo_tienda.json", silencioso=True, escribir_query=False):
            self._set_default_query()

    def _default_query_for(self) -> str | None:
        dq = (self.ejercicio.default_query or "").strip()
        if dq:
            return dq if dq.endswith(";") else dq + ";"
        names = self.engine.table_names()
        if names:
            return f"SELECT * FROM {names[0]};"
        return None

    def _set_default_query(self) -> None:
        q = self._default_query_for()
        if q:
            self.editor.setPlainText(q + "\n")

    def cargar_preset(self, filename: str, silencioso: bool = False, escribir_query: bool = True) -> bool:
        path = os.path.normpath(os.path.join(self._bundle_dir(), "examples", filename))
        if not os.path.exists(path):
            if not silencioso:
                _show_custom_dialog(self, "EJEMPLO NO ENCONTRADO", f"No se encontró:\n{path}")
            return False
        result = load_file(path)
        if not result.ok and not silencioso:
            _show_custom_dialog(self, "ERROR DE DECODIFICACIÓN", "\n".join(result.errors))
        self._aplicar_resultado(result, path, escribir_query=escribir_query)
        return result.ok

    def cargar_json(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "CARGAR EJERCICIO (.json)", "", "JSON (*.json)")
        if not path:
            return
        if not self._confirmar_archivo_grande([path]):
            return
        self._aplicar_resultado(load_file(path), path)

    def _elegir_modo_carga(self) -> str | None:
        """Mini-diálogo custom: EJERCICIO (.json), ARCHIVOS o CARPETA (spec cargar-unificado)."""
        dlg = QDialog(self)
        dlg.setWindowTitle("CARGAR")
        dlg.setMinimumWidth(460)
        dlg.setModal(True)
        lay = QVBoxLayout(dlg)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(12)
        title_lbl = QLabel("CARGAR")
        title_lbl.setObjectName("PanelTitle")
        lay.addWidget(title_lbl)
        msg_lbl = QLabel("¿Qué quieres cargar? (.json, *.csv, *.xlsx, *.xls, *.db)")
        msg_lbl.setWordWrap(True)
        msg_lbl.setObjectName("StatementText")
        lay.addWidget(msg_lbl)
        row = QHBoxLayout()
        row.addStretch()
        eleccion: list[str | None] = [None]
        btn_ej = QPushButton("EJERCICIO")
        btn_ej.setObjectName("PrimaryBtn")
        btn_ej.setToolTip("Cargar un ejercicio desde un archivo .json (formato clásico o IA)")
        btn_ej.clicked.connect(lambda: (eleccion.__setitem__(0, "ejercicio"), dlg.accept()))
        btn_files = QPushButton("ARCHIVOS")
        btn_files.setObjectName("PrimaryBtn")
        btn_files.clicked.connect(lambda: (eleccion.__setitem__(0, "archivos"), dlg.accept()))
        btn_folder = QPushButton("CARPETA")
        btn_folder.setObjectName("GhostBtn")
        btn_folder.clicked.connect(lambda: (eleccion.__setitem__(0, "carpeta"), dlg.accept()))
        btn_cancel = QPushButton("CANCELAR")
        btn_cancel.setObjectName("GhostBtn")
        btn_cancel.clicked.connect(dlg.reject)
        row.addWidget(btn_ej)
        row.addWidget(btn_files)
        row.addWidget(btn_folder)
        row.addWidget(btn_cancel)
        lay.addLayout(row)
        dlg.exec()
        return eleccion[0]

    def cargar_unificado(self) -> None:
        """Entrada del botón CARGAR: despacha según el origen elegido (CU-02)."""
        modo = self._elegir_modo_carga()
        if modo == "ejercicio":
            self.cargar_json()
        elif modo == "archivos":
            self.cargar_tablas_archivos()
        elif modo == "carpeta":
            self.cargar_csv_carpeta()

    def cargar_tablas(self) -> None:
        """Compat: despacha a archivos o carpeta (ignora modo ejercicio)."""
        modo = self._elegir_modo_carga()
        if modo == "archivos":
            self.cargar_tablas_archivos()
        elif modo == "carpeta":
            self.cargar_csv_carpeta()

    def _confirmar_archivo_grande(self, paths: list[str]) -> bool:
        """Pre-aviso RG-05: si los ficheros superan AVISO_MB pide confirmación."""
        try:
            mb = sum(os.path.getsize(p) for p in paths) / (1024 * 1024)
        except OSError:
            return True
        if mb <= self.AVISO_MB:
            return True
        dlg = QDialog(self)
        dlg.setWindowTitle("ARCHIVO GRANDE")
        dlg.setMinimumWidth(420)
        dlg.setModal(True)
        lay = QVBoxLayout(dlg)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(12)
        title_lbl = QLabel("ARCHIVO GRANDE")
        title_lbl.setObjectName("PanelTitle")
        lay.addWidget(title_lbl)
        msg_lbl = QLabel(
            f"Vas a cargar {mb:.0f} MB. Puede tardar varios minutos "
            f"y usar mucha memoria (tope de vista: {self.VISOR_MAX_FILAS} filas)."
        )
        msg_lbl.setWordWrap(True)
        msg_lbl.setObjectName("StatementText")
        lay.addWidget(msg_lbl)
        row = QHBoxLayout()
        row.addStretch()
        ok = QPushButton("CARGAR")
        ok.setObjectName("PrimaryBtn")
        ok.clicked.connect(dlg.accept)
        no = QPushButton("CANCELAR")
        no.setObjectName("GhostBtn")
        no.clicked.connect(dlg.reject)
        row.addWidget(ok)
        row.addWidget(no)
        lay.addLayout(row)
        return dlg.exec() == QDialog.DialogCode.Accepted

    def cargar_tablas_archivos(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "CARGAR TABLAS — archivos *.csv / *.xlsx / *.xls / *.db (UTF-8)",
            "",
            "Tablas (*.csv *.xlsx *.xls *.db *.sqlite *.sqlite3);;Todos los archivos (*.*)",
        )
        if not files:
            return
        if not self._confirmar_archivo_grande(sorted(files)):
            return
        resultados = [load_file(f) for f in sorted(files)]
        merged, reemplazadas = combinar_resultados(resultados)
        self._aplicar_resultado(merged, "; ".join(files))
        if merged.ok and reemplazadas:
            self._toast(
                f"TABLA(S) REEMPLAZADA(S): {', '.join(reemplazadas)} — GANÓ EL ÚLTIMO ARCHIVO"
            )

    def cargar_csv_carpeta(self) -> None:
        folder = QFileDialog.getExistingDirectory(
            self, "CARGAR TABLAS — carpeta con *.csv / *.xlsx / *.xls / *.db (UTF-8)"
        )
        if not folder:
            return
        archivos = [
            os.path.join(folder, f)
            for f in os.listdir(folder)
            if os.path.splitext(f)[1].lower() in (".csv", ".xlsx", ".xls", ".db", ".sqlite", ".sqlite3")
        ]
        if not self._confirmar_archivo_grande(archivos):
            return
        self._aplicar_resultado(load_tablas_folder(folder), folder)

    # Alias nuevo (compat UI / tests)
    def cargar_tablas_carpeta(self) -> None:
        return self.cargar_csv_carpeta()

    def _refresh_status(self) -> None:
        """Barra de estado real: conteos del engine (UN-01/UN-02)."""
        tablas = self.engine.table_names()
        filas = sum(len(t.rows) for t in self.engine.tables.values())
        self.status_db.setText(f"TABLAS: {len(tablas)} · FILAS: {filas} · DB: MEMORIA OK")

    def _aplicar_resultado(self, result, _origen: str, escribir_query: bool = True) -> None:
        if not result.ok:
            msg = "\n".join(result.errors) or "No se pudieron cargar las tablas."
            _show_custom_dialog(self, "ERROR DE DECODIFICACIÓN", msg)
            return
        self._crono_reset()  # CR-05: ejercicio nuevo → crono a cero y detenido
        omitidas = self.engine.load_tables(result.tables) or []
        self.ejercicio = result.ejercicio or Ejercicio()
        self._refresh_tabla_list()
        self._refresh_briefing()
        self._refresh_autocomplete()
        self._refresh_status()
        filas = sum(len(t.rows) for t in result.tables)
        self._toast(f"EJERCICIO CARGADO: {len(result.tables)} TABLA(S), {filas} FILA(S)")
        if escribir_query:
            self._set_default_query()
        self._limpiar_resultado()
        if omitidas:
            # CR-03: el engine descartó tablas (CREATE fallido) → avisar
            self._toast(f"TABLA(S) OMITIDA(S): {', '.join(omitidas)}")
        if result.errors:
            # CA-04: carga parcial (algunos ficheros fallaron) → avisar con nombres
            _show_custom_dialog(self, "ERROR DE DECODIFICACIÓN", "\n".join(result.errors))
