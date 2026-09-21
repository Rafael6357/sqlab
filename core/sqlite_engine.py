"""Motor SQLite embebido. Crea las tablas de la sesión en memoria
y ejecuta consultas SQL reales, devolviendo columnas/filas o un
error amigable (ver core.error_friendly).
"""
from __future__ import annotations

import re
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


def _scalar(value: Any) -> Any:
    """Normaliza un valor para SQLite: deja pasar escalares y convierte el resto a str."""
    if value is None or isinstance(value, (str, int, float, bool, bytes)):
        return value
    return str(value)


# Máscara para literales/comentarios: se sustituyen por \x00N\x00 (sin
# paréntesis ni comillas) para poder escanear operandos a su alrededor.
_MASCARA_RE = re.compile(
    r"'(?:[^']|'')*'|\"(?:[^\"]|\"\")+\"|--[^\n]*|/\*.*?\*/", re.DOTALL
)


def _leer_tipo(s: str, i: int) -> int | None:
    """Fin (exclusivo) del TIPO que empieza en i: palabra + (params) opcional."""
    m = re.match(r"[A-Za-z_][\w$]*", s[i:])
    if not m:
        return None
    j = i + m.end()
    if j < len(s) and s[j] == "(":
        prof = 0
        while j < len(s):
            if s[j] == "(":
                prof += 1
            elif s[j] == ")":
                prof -= 1
                if prof == 0:
                    return j + 1
            j += 1
        return None
    return j


def _leer_operando(s: str, fin: int) -> int | None:
    """Inicio del operando que termina en fin (índice del primer ':').

    Hacia atrás: identificador, marcador \x00N\x00, literal entrecomillado
    o grupo balanceado (+ nombre de función prefijado, ej. CAST(...)).
    """
    i = fin - 1
    while i >= 0 and s[i] in " \t\r\n":
        i -= 1
    if i < 0:
        return None
    if s[i] == ")":
        prof = 0
        while i >= 0:
            if s[i] == ")":
                prof += 1
            elif s[i] == "(":
                prof -= 1
                if prof == 0:
                    break
            i -= 1
        if i < 0:
            return None
        i -= 1
        while i >= 0 and (s[i].isalnum() or s[i] in "_$."):
            i -= 1
        return i + 1
    m = re.search(r"\x00\d+\x00$", s[: i + 1])
    if m:
        return m.start()
    while i >= 0 and (s[i].isalnum() or s[i] in "_$."):
        i -= 1
    if i + 1 >= fin:
        return None
    return i + 1


def _reescribir_cast_postgres(query: str) -> str:
    """Reescribe `expr::TIPO` (Postgres) a `CAST(expr AS TIPO)` (PG-01).

    Enmascara literales/comentarios para no tocarlos; el operando se busca
    con scan balanceado (soporta anidados por iteración). Sin operando o
    tipo válido se deja tal cual.
    """
    literales: list[str] = []

    def _guardar(m: re.Match) -> str:
        literales.append(m.group(0))
        return f"\x00{len(literales) - 1}\x00"

    texto = _MASCARA_RE.sub(_guardar, query)
    for _ in range(10):
        pos = texto.find("::")
        if pos == -1:
            break
        ini = _leer_operando(texto, pos)
        fin_tipo = _leer_tipo(texto, pos + 2) if ini is not None else None
        if ini is None or fin_tipo is None:
            break
        texto = texto[:ini] + f"CAST({texto[ini:pos]} AS {texto[pos + 2:fin_tipo]})" + texto[fin_tipo:]
    for i, lit in enumerate(literales):
        texto = texto.replace(f"\x00{i}\x00", lit)
    return texto


def _partir_sentencias(query: str) -> list[str]:
    """Parte un script por ; fuera de literales '...'/\"...\" y comentarios."""
    partes: list[str] = []
    buf: list[str] = []
    i, n = 0, len(query)
    while i < n:
        ch = query[i]
        nxt = query[i + 1] if i + 1 < n else ""
        if ch in ("'", '"'):
            j = i + 1
            while j < n:
                if query[j] == ch:
                    if j + 1 < n and query[j + 1] == ch:
                        j += 2
                    else:
                        j += 1
                        break
                else:
                    j += 1
            buf.append(query[i:j])
            i = j
        elif ch == "-" and nxt == "-":
            j = query.find("\n", i)
            fin = n if j == -1 else j
            buf.append(query[i:fin])
            i = fin
        elif ch == "/" and nxt == "*":
            j = query.find("*/", i + 2)
            fin = n if j == -1 else j + 2
            buf.append(query[i:fin])
            i = fin
        elif ch == ";":
            partes.append("".join(buf))
            buf = []
            i += 1
        else:
            buf.append(ch)
            i += 1
    partes.append("".join(buf))
    return [p.strip() for p in partes if p.strip()]


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
        """Ejecuta una o varias sentencias (separadas por ;) y devuelve el
        último resultado con filas, o un error traducido (spec fix-multi-sentencia)."""
        if self._conn is None:
            return QueryResult(ok=False, error="Todavía no hay tablas cargadas. Carga un archivo de ejercicio primero.")
        query = _reescribir_cast_postgres(query.strip().strip(";"))
        if not query:
            return QueryResult(ok=True, message="Escribe una consulta y pulsa Ejecutar.")
        sentencias = _partir_sentencias(query)
        ultimo: QueryResult | None = None
        for s in sentencias:
            ultimo = self._ejecutar_una(s)
            if ultimo.error:
                return ultimo
        assert ultimo is not None
        if len(sentencias) > 1 and not ultimo.columns:
            ultimo.message = f"{len(sentencias)} sentencias ejecutadas correctamente."
        return ultimo

    def _ejecutar_una(self, query: str) -> QueryResult:
        """Ejecuta una única sentencia (sin ;) y devuelve su resultado."""
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
            return QueryResult(ok=False, error=friendly_error(str(exc), self.tables.keys(), query))

    def table_names(self) -> list[str]:
        return list(self.tables.keys())

    def column_names(self, table: str) -> list[str]:
        t = self.tables.get(table)
        return [c.name for c in t.columns] if t else []