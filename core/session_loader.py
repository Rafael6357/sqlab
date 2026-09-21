"""Carga archivos de ejercicio (.json, .csv, .xlsx, .xls, .db) y devuelve una lista
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

Formato CSV/XLSX/XLS (carpeta = múltiples tablas):
- Cada archivo .csv / .xlsx / .xls → una tabla (primera hoja en Excel).
- Nombre del archivo (sin extensión) = nombre de tabla (espacios y - → _).
- Primera fila = cabeceras (vacías → col1, duplicadas → _2).
- Tipos inferidos automáticamente.
- CSV: UTF-8 o UTF-8 con BOM, delimitador , o ; auto-detectado, ext. insensible a mayúsculas.
- XLSX/XLS: solo primera hoja, valores tal cual, celdas vacías → None.
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


# Marcadores de nulidad estilo pandas na_values (spec normalizar-nulos-csv-excel).
# Se compara con strip(): cubre "", " ", "-", "NA", "NULL", "null", "NaN".
_NULOS_TEXTO = frozenset({"", "-", "NA", "NULL", "null", "NaN"})


def _es_nulo(value) -> bool:
    """True si el valor es nulo: None o texto marcador (tras strip)."""
    if value is None:
        return True
    return isinstance(value, str) and value.strip() in _NULOS_TEXTO


def _normalize_headers(raw_headers: list) -> list[str]:
    """Normaliza cabeceras: strip, BOM, vacías → colN, duplicadas → _2.

    Dedup case-insensitive (SQLite no distingue Nombre/nombre) y sin comillas
    dobles (romperían el CREATE TABLE entrecomillado).
    """
    cleaned: list[str] = []
    seen: dict[str, int] = {}
    for i, h in enumerate(raw_headers):
        # Excel puede dar None o números; csv da str
        if h is None:
            h_str = ""
        else:
            h_str = str(h).strip().lstrip("\ufeff").strip().replace('"', "")
        if not h_str:
            h_str = f"col{i + 1}"
        # Deduplicar (clave insensible a mayúsculas, conserva el original)
        base = h_str
        key = base.lower()
        count = seen.get(key, 0)
        if count:
            h_str = f"{base}_{count + 1}"
            key = h_str.lower()
        seen[key] = count + 1
        cleaned.append(h_str)
    return cleaned


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
        with open(path, "r", encoding="utf-8-sig") as f:
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
        with open(path, "r", encoding="utf-8-sig", newline="") as f:
            sample = f.read(8192)
            f.seek(0)
            # Auto-detectar delimitador , vs ;
            delimiter = ","
            if sample:
                try:
                    dialect = csv.Sniffer().sniff(sample, delimiters=",;")
                    delimiter = dialect.delimiter
                except csv.Error:
                    # Heurística fallback
                    if sample.count(";") > sample.count(","):
                        delimiter = ";"
            reader = csv.reader(f, delimiter=delimiter)
            rows_all = list(reader)
    except UnicodeDecodeError:
        return LoadResult(ok=False, errors=[f"El archivo «{os.path.basename(path)}» no se pudo leer. Asegúrate de que esté codificado en UTF-8."])
    except OSError as exc:
        return LoadResult(ok=False, errors=[f"No se pudo leer el archivo:\n{exc}"])

    if not rows_all or len(rows_all) < 2:
        return LoadResult(ok=False, errors=[f"El CSV «{os.path.basename(path)}» está vacío o solo tiene cabecera."])

    headers_raw = rows_all[0]
    data_rows = rows_all[1:]
    table_name = Path(path).stem
    table_name = table_name.replace(" ", "_").replace("-", "_")

    headers = _normalize_headers(headers_raw)

    columns: list[Column] = []
    for h in headers:
        columns.append(Column(name=h))

    # Inferir tipos a partir de las primeras filas con datos
    for idx, col in enumerate(columns):
        sample_values = []
        for row in data_rows:
            if idx < len(row):
                v = row[idx].strip() if isinstance(row[idx], str) else str(row[idx]).strip()
                if v:
                    sample_values.append(v)
            if len(sample_values) >= 20:
                break
        types_found = {_infer_type(v) for v in sample_values[:20]}
        if types_found <= {"INTEGER"}:
            col.type = "INTEGER"
        elif types_found <= {"INTEGER", "REAL"}:
            col.type = "REAL"
        else:
            col.type = "TEXT"

    rows: list[list] = []
    for row in data_rows:
        # Normalizar celdas no escalares
        norm = []
        for v in row:
            if isinstance(v, (int, float)):
                norm.append(v)
            elif v is None:
                norm.append(None)
            else:
                norm.append(str(v))
        filled = norm + [None] * (len(columns) - len(norm))
        rows.append([None if _es_nulo(v) else v for v in filled[:len(columns)]])

    table = Table(name=table_name, columns=columns, rows=rows)
    return LoadResult(ok=True, tables=[table], errors=[])


def _parse_excel(path: str) -> LoadResult:
    """Parsea .xlsx (openpyxl) o .xls (xlrd) → tabla de la primera hoja."""
    ext = os.path.splitext(path)[1].lower()
    table_name = Path(path).stem.replace(" ", "_").replace("-", "_")
    rows_all: list[list] = []
    try:
        if ext == ".xlsx":
            import openpyxl
            wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
            ws = wb.active
            if ws is None:
                return LoadResult(ok=False, errors=[f"El Excel «{os.path.basename(path)}» no tiene hojas."])
            for row in ws.iter_rows(values_only=True):
                # iter_rows en read_only puede dar None para filas vacías
                if row is None:
                    continue
                # Convertir tupla a lista; None se mantiene
                rows_all.append(list(row))
            wb.close()
        elif ext == ".xls":
            import xlrd
            wb = xlrd.open_workbook(path, on_demand=True)
            if wb.nsheets == 0:
                return LoadResult(ok=False, errors=[f"El Excel «{os.path.basename(path)}» no tiene hojas."])
            sheet = wb.sheet_by_index(0)
            if sheet.nrows == 0:
                rows_all = []
            else:
                for r in range(sheet.nrows):
                    row_vals = []
                    for c in range(sheet.ncols):
                        cell = sheet.cell(r, c)
                        # xlrd: ctype 0 empty, 1 text, 2 number, 3 date, 4 bool, 5 error
                        if cell.ctype == 0:
                            row_vals.append(None)
                        elif cell.ctype == 2:
                            # number: si es entero exacto, devolver int, si no float
                            v = cell.value
                            if isinstance(v, float) and v.is_integer():
                                row_vals.append(int(v))
                            else:
                                row_vals.append(v)
                        elif cell.ctype == 3:
                            # fecha → string ISO
                            try:
                                import datetime as _dt
                                dt_tuple = xlrd.xldate_as_tuple(cell.value, wb.datemode)
                                # Intentar construir datetime
                                try:
                                    dt = _dt.datetime(*dt_tuple)
                                    row_vals.append(dt.isoformat(sep=" "))
                                except Exception:
                                    row_vals.append(str(cell.value))
                            except Exception:
                                row_vals.append(str(cell.value))
                        else:
                            row_vals.append(cell.value if cell.value != "" else None)
                    rows_all.append(row_vals)
            # wb.release_resources si existe
            try:
                wb.release_resources()
            except Exception:
                pass
        else:
            return LoadResult(ok=False, errors=[f"Formato no soportado: «{ext}»."])
    except OSError as exc:
        return LoadResult(ok=False, errors=[f"No se pudo leer el archivo:\n{exc}"])
    except Exception as exc:
        return LoadResult(ok=False, errors=[f"El Excel «{os.path.basename(path)}» no se pudo leer. Detalles: {exc}"])

    if not rows_all or len(rows_all) < 2:
        # Distinguir vacío vs solo cabecera — mismo mensaje que CSV para consistencia
        return LoadResult(ok=False, errors=[f"El Excel «{os.path.basename(path)}» está vacío o solo tiene cabecera."])

    headers_raw = rows_all[0]
    data_rows = rows_all[1:]
    headers = _normalize_headers(headers_raw)

    columns: list[Column] = [Column(name=h) for h in headers]

    # Inferir tipos
    for idx, col in enumerate(columns):
        sample_values = []
        for row in data_rows:
            if idx < len(row) and row[idx] not in (None, ""):
                sample_values.append(str(row[idx]).strip())
            if len(sample_values) >= 20:
                break
        types_found = {_infer_type(v) for v in sample_values[:20]} if sample_values else set()
        if not types_found:
            col.type = "TEXT"
        elif types_found <= {"INTEGER"}:
            col.type = "INTEGER"
        elif types_found <= {"INTEGER", "REAL"}:
            col.type = "REAL"
        else:
            col.type = "TEXT"

    rows: list[list] = []
    for row in data_rows:
        # Normalizar longitud
        filled = list(row) + [None] * (len(columns) - len(row))
        # Convertir marcadores de nulidad → None, mantener tipos, truncar
        norm = []
        for v in filled[:len(columns)]:
            if _es_nulo(v):
                norm.append(None)
            elif isinstance(v, float) and v.is_integer() and columns[len(norm)].type == "INTEGER":
                # openpyxl puede dar 1.0 para enteros; normalizar si tipo inferido INTEGER
                norm.append(int(v))
            else:
                norm.append(v)
        rows.append(norm)

    table = Table(name=table_name, columns=columns, rows=rows)
    return LoadResult(ok=True, tables=[table], errors=[])


def _parse_db(path: str) -> LoadResult:
    """Vuelca un fichero SQLite existente a tablas en memoria (solo lectura).

    Lee `sqlite_master` (sin tablas `sqlite_%`), esquema vía `PRAGMA
    table_info` y filas con `SELECT *`. Los valores se conservan tal cual
    (`None` intacto; los textos `"NA"`/`"-"` se respetan como dato explícito,
    igual que en JSON). No modifica el fichero (`mode=ro`).
    """
    import sqlite3

    try:
        con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    except sqlite3.Error:
        return LoadResult(ok=False, errors=[f"El archivo «{os.path.basename(path)}» no es una base SQLite válida."])
    try:
        try:
            cur = con.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            )
            nombres = [r[0] for r in cur.fetchall()]
        except sqlite3.Error:
            return LoadResult(ok=False, errors=[f"El archivo «{os.path.basename(path)}» no es una base SQLite válida."])
        if not nombres:
            return LoadResult(ok=False, errors=[f"El archivo «{os.path.basename(path)}» no contiene tablas."])
        tables: list[Table] = []
        for nombre in nombres:
            try:
                info = con.execute(f'PRAGMA table_info("{nombre}")').fetchall()
            except sqlite3.Error:
                continue
            if not info:
                continue
            columns = [Column(name=str(col[1]), type=str(col[2] or "TEXT").upper() or "TEXT") for col in info]
            try:
                filas = [list(r) for r in con.execute(f'SELECT * FROM "{nombre}"').fetchall()]
            except sqlite3.Error:
                continue
            ncols = len(columns)
            norm = []
            for row in filas:
                reg = list(row[:ncols]) + [None] * max(0, ncols - len(row))
                norm.append([_scalar_db(v) for v in reg])
            tables.append(Table(name=nombre, columns=columns, rows=norm))
        if not tables:
            return LoadResult(ok=False, errors=[f"El archivo «{os.path.basename(path)}» no contiene tablas legibles."])
        return LoadResult(ok=True, tables=tables, errors=[])
    finally:
        try:
            con.close()
        except Exception:
            pass


def _scalar_db(value):
    """Normaliza un valor leído de un .db: escalares tal cual (None intacto)."""
    if value is None or isinstance(value, (str, int, float, bool, bytes)):
        return value
    return str(value)


def load_file(path: str) -> LoadResult:
    """Punto de entrada: detecta el formato y delega."""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".json":
        return _parse_json(path)
    elif ext == ".csv":
        return _parse_csv(path)
    elif ext in (".xlsx", ".xls"):
        return _parse_excel(path)
    elif ext in (".db", ".sqlite", ".sqlite3"):
        return _parse_db(path)
    return LoadResult(ok=False, errors=[f"Formato no soportado: «{ext}». Use archivos .json, .csv, .xlsx, .xls o .db."])


def load_tablas_folder(folder: str) -> LoadResult:
    """Carga todos los .csv/.xlsx/.xls/.db de una carpeta → tablas en memoria."""
    p = Path(folder)
    if not p.is_dir():
        return LoadResult(ok=False, errors=[f"No se encontró la carpeta:\n{folder}"])
    # Case-insensitive
    wanted = {".csv", ".xlsx", ".xls", ".db", ".sqlite", ".sqlite3"}
    files = sorted([f for f in p.iterdir() if f.is_file() and f.suffix.lower() in wanted], key=lambda x: x.name.lower())
    if not files:
        return LoadResult(ok=False, errors=[f"No se encontraron archivos *.csv/*.xlsx/*.xls/*.db en:\n{folder}"])

    all_tables: list[Table] = []
    all_errors: list[str] = []
    for f in files:
        result = load_file(str(f))
        all_tables.extend(result.tables)
        all_errors.extend(result.errors)

    return LoadResult(ok=len(all_tables) > 0, tables=all_tables, errors=all_errors)


# Alias histórico (compat)
load_csv_folder = load_tablas_folder


def combinar_resultados(results: list[LoadResult]) -> tuple[LoadResult, list[str]]:
    """Fusiona varios LoadResult (multi-selección de archivos) en uno solo.

    - Last-wins por nombre de tabla (orden de la lista de entrada).
    - Devuelve (merged, reemplazadas) donde reemplazadas lista los nombres
      que aparecían en más de un archivo.
    - ejercicio: el primero no vacío encontrado.
    """
    por_nombre: dict[str, Table] = {}
    orden: list[str] = []
    reemplazadas: list[str] = []
    errores: list[str] = []
    ejercicio: Ejercicio | None = None
    for r in results:
        if ejercicio is None and r.ejercicio and (r.ejercicio.titulo or r.ejercicio.enunciado):
            ejercicio = r.ejercicio
        for t in r.tables:
            if t.name in por_nombre:
                if t.name not in reemplazadas:
                    reemplazadas.append(t.name)
            else:
                orden.append(t.name)
            por_nombre[t.name] = t
        errores.extend(r.errors)
    tablas = [por_nombre[n] for n in orden]
    return LoadResult(ok=len(tablas) > 0, ejercicio=ejercicio, tables=tablas, errors=errores), reemplazadas
