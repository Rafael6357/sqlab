"""Carga archivos de ejercicio (.json y .csv) y devuelve una lista
de Table (core.sqlite_engine) lista para inyectar en la BD embebida.

Formato JSON (un archivo = una sesión):
{
  "ejercicio": {
    "titulo": "Práctica 01",
    "enunciado": "Selecciona...",
    "pista": "Usa WHERE...",
    "dificultad": "Principiante"
  },
  "tablas": [
    {
      "nombre": "productos",
      "columnas": [
        {"nombre": "id", "tipo": "INTEGER"},
        ...
      ],
      "filas": [[1, "Laptop", 1200.5], ...]
    }
  ]
}

Formato IA alternativo (generado por IA, ver diálogo "Ver Formato JSON IA"):
{
  "title": "Título del ejercicio",
  "difficulty": "Principiante",
  "statement": "Consigna...",
  "expected_hint": "Pista...",
  "tables": [
    {"name": "t", "schema": {"id": "INTEGER PRIMARY KEY", "nombre": "TEXT"},
     "data": [[1, "Ana"], ...]}
  ]
}

Formato CSV (múltiples archivos = múltiples tablas):
- Cada archivo .csv → una tabla.
- Nombre del archivo = nombre de tabla.
- Primera fila = cabeceras.
- Tipos inferidos automáticamente.
"""
from __future__ import annotations

import csv
import json
import os
from dataclasses import dataclass, field
from pathlib import Path

from core.sqlite_engine import Column, Table

_VALID_TYPES = {"INTEGER", "REAL", "TEXT", "NUMERIC", "DATE", "BOOLEAN"}


@dataclass
class Ejercicio:
    titulo: str = ""
    enunciado: str = ""
    pista: str = ""
    dificultad: str = "Principiante"
    default_query: str = ""


@dataclass
class LoadResult:
    ok: bool
    ejercicio: Ejercicio | None = None
    tables: list[Table] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def _infer_type(value: str) -> str:
    """Inferir el tipo SQLite más adecuado para un valor textual."""
    if value in ("", "null", "NULL", "None", "none"):
        return "TEXT"
    try:
        int(value)
        return "INTEGER"
    except ValueError:
        pass
    try:
        float(value)
        return "REAL"
    except ValueError:
        pass
    return "TEXT"


def _normalize_ia_format(raw: dict) -> dict:
    """Convierte formato IA {title,difficulty,statement,expected_hint,tables[]} al formato interno.

    Formato IA:
      {"title": ..., "difficulty": ..., "statement": ..., "expected_hint": ...,
       "tables": [{"name": ..., "schema": {"col": "TYPE"}, "data": [[...]]}]}
    Formato interno:
      {"ejercicio": {"titulo": ..., "enunciado": ..., "pista": ..., "dificultad": ...},
       "tablas": [{"nombre": ..., "columnas": [{"nombre":..., "tipo":...}], "filas": [...]}]}
    """
    ia_tables = raw.get("tables", [])
    if not isinstance(ia_tables, list):
        return raw
    ejercicio = {
        "titulo": raw.get("title", ""),
        "enunciado": raw.get("statement", ""),
        "pista": raw.get("expected_hint", ""),
        "dificultad": raw.get("difficulty", "Principiante"),
        "default_query": raw.get("defaultQuery", raw.get("default_query", "")),
    }
    tablas = []
    for tbl in ia_tables:
        if not isinstance(tbl, dict):
            continue
        schema = tbl.get("schema", {})
        if isinstance(schema, dict):
            columnas = [{"nombre": k, "tipo": str(v).upper()} for k, v in schema.items()]
        elif isinstance(schema, list):
            columnas = schema
        else:
            columnas = []
        tablas.append({
            "nombre": tbl.get("name", ""),
            "columnas": columnas,
            "filas": tbl.get("data", []),
        })
    return {"ejercicio": ejercicio, "tablas": tablas}


def _parse_json(path: str) -> LoadResult:
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except json.JSONDecodeError as exc:
        return LoadResult(ok=False, errors=[f"El archivo no es JSON válido.\nDetalles: {exc}"])
    except OSError as exc:
        return LoadResult(ok=False, errors=[f"No se pudo leer el archivo:\n{exc}"])

    if not isinstance(raw, dict):
        return LoadResult(ok=False, errors=["El JSON debe ser un objeto con claves «tablas» o «tables»."])
    # Adapter: si viene en formato IA (title/tables) lo normalizamos.
    if "tablas" not in raw and "tables" in raw:
        raw = _normalize_ia_format(raw)

    errors: list[str] = []
    ejercicio_data = raw.get("ejercicio", {})
    ejercicio = Ejercicio(
        titulo=ejercicio_data.get("titulo", ""),
        enunciado=ejercicio_data.get("enunciado", ""),
        pista=ejercicio_data.get("pista", ""),
        dificultad=ejercicio_data.get("dificultad", "Principiante") or "Principiante",
        default_query=ejercicio_data.get("default_query", raw.get("defaultQuery", "")) or "",
    )
    tablas_raw = raw.get("tablas", [])
    if not tablas_raw:
        errors.append("El JSON no contiene ninguna tabla bajo la clave \"tablas\" (o \"tables\" en formato IA).")
        return LoadResult(ok=False, errors=errors)
    if not isinstance(tablas_raw, list):
        errors.append("\"tablas\" debe ser una lista de tablas, no se pudo cargar el ejercicio.")
        return LoadResult(ok=False, errors=errors)

    tables: list[Table] = []
    for i, tbl in enumerate(tablas_raw):
        if not isinstance(tbl, dict):
            errors.append(f"Tabla #{i + 1}: entrada inválida (se esperaba un objeto con «nombre», «columnas» y «filas»).")
            continue
        name = tbl.get("nombre", "")
        if not name or not name.replace("_", "").replace(" ", "_").isalnum():
            errors.append(f"Tabla #{i + 1}: nombre inválido «{name}». Use solo letras, números y guiones bajos.")
            continue
        cols_raw = tbl.get("columnas", [])
        rows_raw = tbl.get("filas", [])
        if isinstance(cols_raw, list) and not cols_raw:
            errors.append(f"Tabla «{name}»: no tiene columnas.")
            continue
        if not isinstance(cols_raw, list):
            errors.append(f"Tabla «{name}»: «columnas» debe ser una lista.")
            continue
        if not isinstance(rows_raw, list):
            errors.append(f"Tabla «{name}»: «filas» debe ser una lista de filas.")
            continue
        columns: list[Column] = []
        for c in cols_raw:
            if not isinstance(c, dict):
                errors.append(f"Tabla «{name}»: se encontró una columna inválida (se esperaba un objeto con «nombre»).")
                continue
            col_name = c.get("nombre")
            if not col_name:
                errors.append(f"Tabla «{name}»: una columna no tiene «nombre».")
                continue
            raw_type = str(c.get("tipo", "TEXT")).upper().strip()
            base = raw_type.split()[0] if raw_type else "TEXT"
            if base not in _VALID_TYPES:
                raw_type = "TEXT"
            columns.append(Column(name=col_name, type=raw_type))
        if not columns:
            errors.append(f"Tabla «{name}»: no se pudo cargar ninguna columna válida.")
            continue
        rows: list[list] = []
        for j, row in enumerate(rows_raw):
            if not isinstance(row, list):
                errors.append(f"Tabla «{name}», fila {j + 1}: se esperaba una lista, se obtuvo {type(row).__name__}.")
                continue
            rows.append([v if v != "" else None for v in row])
        tables.append(Table(name=name, columns=columns, rows=rows))

    return LoadResult(ok=len(tables) > 0, ejercicio=ejercicio, tables=tables, errors=errors)


def _parse_csv(path: str) -> LoadResult:
    """Parsea un único archivo CSV → una tabla cuyo nombre es el nombre del archivo."""
    try:
        with open(path, "r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            rows_all = list(reader)
    except UnicodeDecodeError:
        return LoadResult(ok=False, errors=[f"El archivo «{os.path.basename(path)}» no se pudo leer. Asegúrate de que esté codificado en UTF-8."])
    except OSError as exc:
        return LoadResult(ok=False, errors=[f"No se pudo leer el archivo:\n{exc}"])

    if not rows_all or len(rows_all) < 2:
        return LoadResult(ok=False, errors=[f"El CSV «{os.path.basename(path)}» está vacío o solo tiene cabecera."])

    headers = rows_all[0]
    data_rows = rows_all[1:]
    table_name = Path(path).stem
    table_name = table_name.replace(" ", "_").replace("-", "_")

    columns: list[Column] = []
    for h in headers:
        h_clean = h.strip()
        columns.append(Column(name=h_clean))

    # Inferir tipos a partir de la primera fila con datos
    for idx, col in enumerate(columns):
        sample_values = [row[idx] for row in data_rows if idx < len(row) and row[idx].strip()]
        types_found = {_infer_type(v) for v in sample_values[:20]}
        if types_found <= {"INTEGER"}:
            col.type = "INTEGER"
        elif types_found <= {"INTEGER", "REAL"}:
            col.type = "REAL"
        else:
            col.type = "TEXT"

    rows: list[list] = []
    for row in data_rows:
        filled = row + [""] * (len(columns) - len(row))
        rows.append([v if v != "" else None for v in filled[:len(columns)]])

    table = Table(name=table_name, columns=columns, rows=rows)
    return LoadResult(ok=True, tables=[table], errors=[])


def load_file(path: str) -> LoadResult:
    """Punto de entrada: detecta el formato y delega."""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".json":
        return _parse_json(path)
    elif ext == ".csv":
        return _parse_csv(path)
    return LoadResult(ok=False, errors=[f"Formato no soportado: «{ext}». Use archivos .json o .csv."])


def load_csv_folder(folder: str) -> LoadResult:
    """Carga todos los .csv de una carpeta → una tabla por archivo."""
    csv_files = sorted(Path(folder).glob("*.csv"))
    if not csv_files:
        return LoadResult(ok=False, errors=[f"No se encontraron archivos .csv en:\n{folder}"])

    all_tables: list[Table] = []
    all_errors: list[str] = []
    for csv_file in csv_files:
        result = load_file(str(csv_file))
        all_tables.extend(result.tables)
        all_errors.extend(result.errors)

    return LoadResult(ok=len(all_tables) > 0, tables=all_tables, errors=all_errors)
