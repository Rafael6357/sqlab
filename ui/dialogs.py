"""Diálogos custom dark de SQLab (sin QMessageBox genérico de Windows)."""
from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


def _show_custom_dialog(parent: QWidget, title: str, msg: str, kind: str = "warning") -> None:
    """Diálogo modal dark que reemplaza QMessageBox genérico de Windows."""
    dlg = QDialog(parent)
    dlg.setWindowTitle(title)
    dlg.setMinimumWidth(420)
    dlg.setModal(True)
    lay = QVBoxLayout(dlg)
    lay.setContentsMargins(16, 16, 16, 16)
    lay.setSpacing(12)
    title_lbl = QLabel(title)
    title_lbl.setObjectName("PanelTitle")
    lay.addWidget(title_lbl)
    msg_lbl = QLabel(msg)
    msg_lbl.setWordWrap(True)
    msg_lbl.setObjectName("StatementText")
    lay.addWidget(msg_lbl)
    row = QHBoxLayout()
    row.addStretch()
    btn = QPushButton("ACEPTAR")
    btn.setObjectName("PrimaryBtn")
    btn.setFixedWidth(120)
    btn.clicked.connect(dlg.accept)
    row.addWidget(btn)
    lay.addLayout(row)
    dlg.exec()


CLAUDE_PROMPT = (
    "Actúa como mi profesor de SQL y diseñador de ejercicios.\n"
    "Dame un ejercicio sobre [TEMA, ej: JOINs y GROUP BY] para practicar en mi terminal offline SQLab.\n"
    "Entrégame ÚNICAMENTE un bloque de código JSON con este formato exacto:\n\n"
    "{\n"
    '  "title": "Título del ejercicio",\n'
    '  "difficulty": "Principiante",\n'
    '  "statement": "Consigna clara del problema...",\n'
    '  "expected_hint": "Pista conceptual para resolverlo...",\n'
    '  "tables": [\n'
    "    {\n"
    '      "name": "nombre_tabla",\n'
    '      "schema": {\n'
    '        "columna1": "INTEGER PRIMARY KEY",\n'
    '        "columna2": "TEXT",\n'
    '        "columna3": "REAL"\n'
    "      },\n"
    '      "data": [\n'
    '        [1, "Texto ejemplo", 99.50],\n'
    '        [2, "Otro registro", 120.00]\n'
    "      ]\n"
    "    }\n"
    "  ]\n"
    "}"
)
