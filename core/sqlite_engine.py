"""Motor SQLite embebido. Crea las tablas de la sesión en memoria
y ejecuta consultas SQL reales, devolviendo columnas/filas o un
error amigable (ver core.error_friendly).
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from typing import Any

from core.error_friendly import friendly_error


@dataclass
class Column:
    name: str
    type: str = "TEXT"  # INTEGER, REAL, TEXT, NUMERIC, DATE


@dataclass
class Table:
    name: str
    columns: list[Column]
    rows: list[list[Any]]


@dataclass
class QueryResult:
    ok: bool
    columns: list[str] = field(default_factory=list)
    rows: list[list[Any]] = field(default_factory=list)
    row_count: int = 0
    message: str = ""
    error: str = ""


def _valid_identifier(name: str) -> bool:
    return bool(name) and name.replace("_", "").isalnum() and name[0].isalpha() or name.startswith("_")


def _scalar(value: Any) -> Any:
    """Normaliza un valor para SQLite: deja pasar escalares y convierte el resto a str."""
    if value is None or isinstance(value, (str, int, float, bool, bytes)):
        return value
    return str(value)


class SQLEngine:
    """Mantiene una base SQLite en memoria con las tablas de la sesión activa."""

    def __init__(self) -> None:
        self._conn: sqlite3.Connection | None = None
        self.tables: dict[str, Table] = {}
        self.version: str = ""

    @property
    def connected(self) -> bool:
        return self._conn is not None

    def close(self) -> None:
        """Cierra la conexión y descarta las tablas de la sesión (SC-10)."""
        if self._conn is not None:
            self._conn.close()
            self._conn = None
        self.tables = {}

    def load_tables(self, tables: list[Table]) -> list[str]:
        """Sustituye la sesión actual por un nuevo conjunto de tablas.

        Cada tabla se crea de forma independiente: si una falla (CREATE)
        se omite sin romper el resto. Devuelve los nombres omitidos (CR-03).
        """
        self.close()
        self.tables = {}
        omitidas: list[str] = []
        if not tables:
            return omitidas
        self._conn = sqlite3.connect(":memory:")
        self._conn.row_factory = sqlite3.Row
        for t in tables:
            if not t.columns:
                omitidas.append(t.name)
                continue
            cols = ", ".join(
                f'"{c.name}" {c.type}' for c in t.columns
            )
            try:
                self._conn.execute(f'CREATE TABLE "{t.name}" ({cols});')
            except sqlite3.Error:
                omitidas.append(t.name)
                continue
            ncols = len(t.columns)
            qmarks = ", ".join("?" for _ in range(ncols))
            lote = []
            for row in t.rows:
                row_norm = [None] * ncols
                for i, v in enumerate(row[:ncols]):
                    row_norm[i] = _scalar(v)
                lote.append(tuple(row_norm))
            try:
                # Ruta rápida por lotes (RG-06)
                self._conn.executemany(
                    f'INSERT INTO "{t.name}" VALUES ({qmarks})', lote
                )
            except sqlite3.Error:
                # Fallback fila por fila: omite inválidas sin romper el lote
                for row_norm in lote:
                    try:
                        self._conn.execute(
                            f'INSERT INTO "{t.name}" VALUES ({qmarks})', row_norm
                        )
                    except sqlite3.Error:
                        continue
            self.tables[t.name] = t
        self._conn.commit()
        return omitidas

    def execute(self, query: str) -> QueryResult:
        """Ejecuta una consulta y devuelve el resultado o un error traducido."""
        if self._conn is None:
            return QueryResult(ok=False, error="Todavía no hay tablas cargadas. Carga un archivo de ejercicio primero.")
        query = query.strip().strip(";")
        if not query:
            return QueryResult(ok=True, message="Escribe una consulta y pulsa Ejecutar.")
        try:
            cursor = self._conn.execute(query)
            try:
                rows = [list(r) for r in cursor.fetchall()]
            except sqlite3.ProgrammingError:
                rows = []
            columns = [d[0] for d in (cursor.description or [])]
            self._conn.commit()
            return QueryResult(
                ok=True,
                columns=columns,
                rows=rows,
                row_count=len(rows),
                message=f"Consulta ejecutada correctamente. {len(rows)} fila(s)",
            )
        except sqlite3.Error as exc:
            return QueryResult(ok=False, error=friendly_error(str(exc), self.tables.keys()))

    def table_names(self) -> list[str]:
        return list(self.tables.keys())

    def column_names(self, table: str) -> list[str]:
        t = self.tables.get(table)
        return [c.name for c in t.columns] if t else []