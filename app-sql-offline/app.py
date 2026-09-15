"""SQLab — Laboratorio offline para practicar SQL.

Requiere: PySide6 (ver requirements.txt).
Ejecutar:  python app.py
"""
from __future__ import annotations

import os
import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication


def _load_stylesheet(app: QApplication) -> None:
    qss_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "dark.qss")
    try:
        with open(qss_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except OSError:
        print("Aviso: no se encontró dark.qss, la app usará el tema por defecto.")


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("SQLab")
    app.setOrganizationName("SQLPractica")
    logo = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "logo_sqllab.svg")
    if os.path.exists(logo):
        app.setWindowIcon(QIcon(logo))

    from ui.main_window import MainWindow

    _load_stylesheet(app)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())