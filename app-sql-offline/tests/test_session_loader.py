"""Tests unitarios de core/session_loader.py — sin dependencia Qt."""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import pytest
from core.session_loader import (
    Ejercicio,
    LoadResult,
    _infer_type,
    _normalize_ia_format,
    load_csv_folder,
    load_file,
)
from core.sqlite_engine import Column, Table

EXAMPLES = os.path.join(os.path.dirname(__file__), "..", "examples")


# ── _infer_type ────────────────────────────────────────────────────────

def test_infer_type_integer():
    assert _infer_type("42") == "INTEGER"


def test_infer_type_real():
    assert _infer_type("3.14") == "REAL"


def test_infer_type_text():
    assert _infer_type("hola") == "TEXT"


def test_infer_type_empty():
    assert _infer_type("") == "TEXT"


def test_infer_type_null():
    assert _infer_type("null") == "TEXT"
    assert _infer_type("NULL") == "TEXT"
    assert _infer_type("None") == "TEXT"


# ── _normalize_ia_format ──────────────────────────────────────────────

def test_normalize_ia_format_full():
    raw = {
        "title": "Ejercicio IA",
        "difficulty": "Intermedio",
        "statement": "Haz un JOIN",
        "expected_hint": "Pista IA",
        "tables": [
            {
                "name": "usuarios",
                "schema": {"id": "INTEGER PRIMARY KEY", "nombre": "TEXT"},
                "data": [[1, "Ana"]],
            }
        ],
    }
    result = _normalize_ia_format(raw)
    assert result["ejercicio"]["titulo"] == "Ejercicio IA"
    assert result["ejercicio"]["enunciado"] == "Haz un JOIN"
    assert result["ejercicio"]["pista"] == "Pista IA"
    assert result["ejercicio"]["dificultad"] == "Intermedio"
    assert len(result["tablas"]) == 1
    assert result["tablas"][0]["nombre"] == "usuarios"
    assert result["tablas"][0]["columnas"][0]["nombre"] == "id"
    assert result["tablas"][0]["columnas"][0]["tipo"] == "INTEGER PRIMARY KEY"
    assert result["tablas"][0]["filas"] == [[1, "Ana"]]


def test_normalize_ia_format_no_tables():
    raw = {"title": "Test"}
    result = _normalize_ia_format(raw)
    # Sin "tables" → raw.get("tables", []) es [] (list), se normaliza igual
    assert "ejercicio" in result
    assert result["ejercicio"]["titulo"] == "Test"
    assert result["tablas"] == []


def test_normalize_ia_format_default_query():
    raw = {
        "title": "T",
        "difficulty": "D",
        "statement": "S",
        "expected_hint": "H",
        "defaultQuery": "SELECT 1;",
        "tables": [],
    }
    result = _normalize_ia_format(raw)
    assert result["ejercicio"]["default_query"] == "SELECT 1;"


# ── load_file: JSON interno ────────────────────────────────────────────

def test_load_json_tienda():
    path = os.path.join(EXAMPLES, "ejemplo_tienda.json")
    r = load_file(path)
    assert r.ok
    assert len(r.tables) == 2
    names = {t.name for t in r.tables}
    assert names == {"clientes", "pedidos"}
    assert r.ejercicio is not None
    assert "Gasto" in r.ejercicio.titulo
    assert r.ejercicio.dificultad


def test_load_json_biblioteca():
    path = os.path.join(EXAMPLES, "ejemplo_biblioteca.json")
    r = load_file(path)
    assert r.ok
    assert len(r.tables) == 3
    assert {t.name for t in r.tables} == {"libros", "usuarios", "prestamos"}


# ── load_file: JSON formato IA ─────────────────────────────────────────

def test_load_json_ia_format(tmp_path):
    ia_data = {
        "title": "IA Exercise",
        "difficulty": "Principiante",
        "statement": "Haz un SELECT",
        "expected_hint": "Pista",
        "tables": [
            {
                "name": "items",
                "schema": {"id": "INTEGER", "name": "TEXT"},
                "data": [[1, "a"], [2, "b"]],
            }
        ],
    }
    path = tmp_path / "ia_exercise.json"
    path.write_text(json.dumps(ia_data), encoding="utf-8")
    r = load_file(str(path))
    assert r.ok
    assert len(r.tables) == 1
    assert r.tables[0].name == "items"
    assert len(r.tables[0].rows) == 2


# ── load_file: errores ────────────────────────────────────────────────

def test_load_json_invalid(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{not valid json", encoding="utf-8")
    r = load_file(str(path))
    assert not r.ok
    assert any("json" in e.lower() for e in r.errors)


def test_load_json_no_tables(tmp_path):
    path = tmp_path / "empty.json"
    path.write_text(json.dumps({"ejercicio": {"titulo": "X"}}), encoding="utf-8")
    r = load_file(str(path))
    assert not r.ok


def test_load_json_tablas_not_list(tmp_path):
    path = tmp_path / "tablas_dict.json"
    path.write_text(json.dumps({"tablas": {"clientes": {}}}), encoding="utf-8")
    r = load_file(str(path))
    assert not r.ok


def test_load_json_tabla_not_dict(tmp_path):
    path = tmp_path / "tabla_int.json"
    path.write_text(json.dumps({"tablas": [42]}), encoding="utf-8")
    r = load_file(str(path))
    assert not r.ok


def test_load_json_campo_no_dict(tmp_path):
    path = tmp_path / "campo_str.json"
    path.write_text(json.dumps({"tablas": [{"nombre": "t", "columnas": ["id"], "filas": []}]}), encoding="utf-8")
    r = load_file(str(path))
    assert not r.ok


def test_load_json_campo_sin_nombre(tmp_path):
    path = tmp_path / "campo_sin_nombre.json"
    path.write_text(json.dumps({"tablas": [{"nombre": "t", "columnas": [{"tipo": "INTEGER"}], "filas": []}]}), encoding="utf-8")
    r = load_file(str(path))
    assert not r.ok


def test_load_json_filas_no_lista(tmp_path):
    path = tmp_path / "filas_dict.json"
    path.write_text(json.dumps({"tablas": [{"nombre": "t", "columnas": [{"nombre": "a", "tipo": "INTEGER"}], "filas": {"a": 1}}]}), encoding="utf-8")
    r = load_file(str(path))
    assert not r.ok


def test_load_unsupported_format(tmp_path):
    path = tmp_path / "data.xml"
    path.write_text("<root/>", encoding="utf-8")
    r = load_file(str(path))
    assert not r.ok
    assert any("formato" in e.lower() for e in r.errors)


# ── load_file: CSV ────────────────────────────────────────────────────

def test_load_csv():
    path = os.path.join(EXAMPLES, "csv", "clientes.csv")
    r = load_file(path)
    assert r.ok
    assert len(r.tables) == 1
    t = r.tables[0]
    assert t.name == "clientes"
    assert len(t.columns) == 4
    assert t.columns[0].name == "id"
    assert t.columns[0].type == "INTEGER"
    assert len(t.rows) == 4


# ── load_csv_folder ───────────────────────────────────────────────────

def test_load_csv_folder():
    folder = os.path.join(EXAMPLES, "csv")
    r = load_csv_folder(folder)
    assert r.ok
    names = {t.name for t in r.tables}
    assert names == {"clientes", "productos"}


def test_load_csv_folder_empty(tmp_path):
    r = load_csv_folder(str(tmp_path))
    assert not r.ok
    assert any("csv" in e.lower() for e in r.errors)


# ── Ejercicio defaults ────────────────────────────────────────────────

def test_ejercicio_defaults():
    e = Ejercicio()
    assert e.titulo == ""
    assert e.enunciado == ""
    assert e.pista == ""
    assert e.dificultad == "Principiante"
