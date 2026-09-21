"""Spec ui-nombres-estado — renombres, barra de estado real, maximizada."""
from __future__ import annotations

import re

import pytest
from PySide6.QtWidgets import QCheckBox, QLabel, QPushButton, QTabWidget, QToolButton

NUEVOS = [
    "CARGAR TABLAS",
    "CONTENIDO DE LA TABLA",
    "HISTORIAL DE CONSULTAS",
    "ESQUEMA DE TABLAS",
    "RESULTADO DE LA CONSULTA",
    "EJERCICIO",
    "FORMATO SQL",
    "GUARDAR SESIÓN",
    "CARGAR SESIÓN",
    "AUTOCOMPLETAR",
    "PISTA:",
    "TABLA ACTIVA:",
    "PLANTILLA JSON PARA IA",
]

# Textos exactos que deben haber desaparecido (match exacto, no subcadena)
VIEJOS_EXACTOS = [
    "TABLAS",
    "VOLCADO DE TABLA",
    "> REGISTRO DE TRANSACCIONES",
    "> MATRIZ DE ESQUEMA",
    ">> MATRIZ DE RESULTADOS",
    "[DIRECTIVA DE MISIÓN]",
    "FORMATO",
    "SAV",
    "SES",
    "AC",
    "[IA_DESCIFRADO]",
    "PROTOCOLO DE SUGERENCIA:",
    "NODO:",
    "MEMORIA: OK",
    "FORMATO JSON IA",
    "CACHÉ_TX: SINCRONIZADA",
    "PRAGMA: DESACTIVADO",
    "EN MEMORIA",
]


def _textos_visibles(app) -> list[str]:
    textos: list[str] = []
    for b in app.findChildren(QPushButton):
        textos.append(b.text())
    for c in app.findChildren(QCheckBox):
        textos.append(c.text())
    for t in app.findChildren(QToolButton):
        textos.append(t.text())
    for lab in app.findChildren(QLabel):
        textos.append(lab.text())
    for tabs in app.findChildren(QTabWidget):
        for i in range(tabs.count()):
            textos.append(tabs.tabText(i))
    return textos


@pytest.mark.parametrize("esperado", NUEVOS)
def test_nombres_nuevos_presentes(app, esperado):
    """Cada texto nuevo aparece en algún widget visible."""
    textos = _textos_visibles(app)
    if esperado == "EJERCICIO":
        assert any(t == "[EJERCICIO]" for t in textos), "falta tab [EJERCICIO]"
    elif esperado == "PISTA:":
        assert any(t == "PISTA:" for t in textos), "falta label PISTA:"
    else:
        assert any(esperado in t for t in textos), f"falta texto nuevo: {esperado}"


@pytest.mark.parametrize("viejo", VIEJOS_EXACTOS)
def test_nombres_viejos_ausentes(app, viejo):
    """Ningún widget muestra ya los textos viejos (match exacto)."""
    assert all(t != viejo for t in _textos_visibles(app)), f"sigue visible: {viejo}"


def test_registros_plural(app):
    """El encabezado ya no muestra el conteo 'N REGISTROS'."""
    app.cargar_preset("ejemplo_tienda.json")
    assert not hasattr(app, "row_count_label")
    textos = _textos_visibles(app)
    assert not any(re.fullmatch(r"\d+ REGISTROS", texto or "") for texto in textos)


def test_hint_error_menciona_esquema(app):
    app.editor.setPlainText("SELEKT * FROM nada;")
    app.ejecutar_consulta()
    assert "MATRIZ DE ESQUEMA" not in app.error_hint.text()
    assert "ESQUEMA DE TABLAS" in app.error_hint.text()


def test_status_db_formato_y_actualizacion(app):
    """UN-01/02: barra real con formato y actualización tras carga y ejecución."""
    assert hasattr(app, "status_db")
    app.cargar_preset("ejemplo_tienda.json")
    n_tablas = len(app.engine.table_names())
    n_filas = sum(len(t.rows) for t in app.engine.tables.values())
    assert app.status_db.text() == f"TABLAS: {n_tablas} · FILAS: {n_filas} · DB: MEMORIA OK"
    app.editor.setPlainText("SELECT * FROM clientes;")
    app.ejecutar_consulta()
    assert app.status_db.text() == f"TABLAS: {n_tablas} · FILAS: {n_filas} · DB: MEMORIA OK"


def test_app_arranca_maximizada():
    """UN-03: app.py usa showMaximized."""
    import os
    path = os.path.join(os.path.dirname(__file__), "..", "app.py")
    with open(path, encoding="utf-8") as fh:
        texto = fh.read()
    assert "showMaximized" in texto, "app.py no usa showMaximized"


def test_tooltip_cargar_tablas_menciona_archivos_y_carpeta(app):
    tip = app.btn_csv.toolTip()
    assert "ARCHIVOS" in tip.upper() or "ARCHIVO" in tip.upper()
    assert "CARPETA" in tip.upper()
    assert "*.csv" in tip and "*.xlsx" in tip
