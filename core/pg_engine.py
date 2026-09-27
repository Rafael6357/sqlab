"""Motor PostgreSQL embebido (spec pg-engine, F1 migración).

Servidor local efímero: cluster template cacheado (initdb una sola vez),
`postgres.exe` directo vía Popen + poll TCP (pg_ctl se cuelga: ver spec
postgres-embebido-spike), BD de sesión `sqllab_<pid>` con DROP al cerrar.

Paridad de API con `SQLEngine`: `execute()` multi-sentencia, `load_tables()`
que devuelve omitidas, `table_names()`/`column_names()`, `exportar_db`.
"""
from __future__ import annotations

import os
import socket
import subprocess
import sys
import tempfile
import time
from typing import Any

from core.error_friendly import friendly_error
from core.sqlite_engine import QueryResult, Table, _partir_sentencias

PG_VERSION = "17"
_TEMPLATE_DIR = f"sqllab-pgdata-{PG_VERSION}"

_TIPOS_PG = {
    "INTEGER", "BIGINT", "SMALLINT", "REAL", "DOUBLE PRECISION",
    "TEXT", "NUMERIC", "DECIMAL", "BOOLEAN", "DATE", "TIMESTAMP",
    "TIME", "BYTEA", "VARCHAR", "CHAR",
}


def _pg_bin_dir() -> str | None:
    """Carpeta con initdb/postgres: vendor en dev, _MEIPASS en exe frozen."""
    dev = r"D:\pg-bin\vendor\pgsql\bin"
    if os.path.isfile(os.path.join(dev, "initdb.exe")):
        return dev
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        frozen = os.path.join(meipass, "pgsql", "bin")
        if os.path.isfile(os.path.join(frozen, "initdb.exe")):
            return frozen
    return None


PG_BIN_DIR = _pg_bin_dir()


def _tipo_pg(tipo: str) -> str:
    """Mapea tipo declarado a tipo PG válido (resto → TEXT)."""
    u = (tipo or "").strip().upper()
    if u.startswith(("VARCHAR", "CHAR", "CHARACTER")):
        return u
    base = u.split("(")[0].strip()
    return base if base in _TIPOS_PG else "TEXT"


def _valor_pg(value: Any) -> Any:
    """Normaliza un valor para psycopg: escalares tal cual (None intacto)."""
    if value is None or isinstance(value, (str, int, float, bool, bytes)):
        return value
    return str(value)


def _puerto_libre() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class PGEngine:
    """Sesión PostgreSQL embebida con la API de SQLEngine."""

    def __init__(self, base_dir: str | None = None, usuario: str = "postgres") -> None:
        import psycopg  # dependencia declarada (requirements.txt)

        if PG_BIN_DIR is None:
            raise RuntimeError("Sin binarios PostgreSQL vendoreados.")
        self._psycopg = psycopg
        self.base = base_dir or os.path.join(tempfile.gettempdir(), _TEMPLATE_DIR)
        self.usuario = usuario
        self.dbname = f"sqllab_{os.getpid()}"
        self.tables: dict[str, Table] = {}
        self._proc: subprocess.Popen | None = None
        self._conn = None
        self.puerto = _puerto_libre()
        self._env = dict(os.environ)
        self._env["LC_ALL"] = "C"
        self._env["LANG"] = "C"
        self._asegurar_cluster()
        self._arrancar()
        self._crear_bd_sesion()

    # ---------------------------------------------------------- ciclo de vida

    @property
    def connected(self) -> bool:
        return self._conn is not None

    def _exe(self, nombre: str) -> str:
        assert PG_BIN_DIR is not None
        return os.path.join(PG_BIN_DIR, nombre)

    def _asegurar_cluster(self) -> None:
        """initdb solo si el template no existe (9 s la primera vez)."""
        if os.path.isfile(os.path.join(self.base, "PG_VERSION")):
            return
        os.makedirs(self.base, exist_ok=True)
        r = subprocess.run(
            [self._exe("initdb.exe"), "-D", self.base, "-E", "UTF8",
             "-U", self.usuario, "--auth=trust"],
            capture_output=True, text=True, env=self._env,
            cwd=PG_BIN_DIR, timeout=300,
        )
        if r.returncode != 0:
            raise RuntimeError(f"initdb falló:\n{(r.stdout + r.stderr)[-1500:]}")

    def dsn(self, db: str | None = None) -> str:
        base = f"host=127.0.0.1 port={self.puerto} user={self.usuario}"
        return f"{base} dbname={db or self.dbname}"

    def _arrancar(self) -> None:
        self._proc = subprocess.Popen(
            [self._exe("postgres.exe"), "-D", self.base, "-p", str(self.puerto),
             "-c", "listen_addresses=127.0.0.1"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            env=self._env, cwd=PG_BIN_DIR,
        )
        t0 = time.time()
        ultimo_error: Exception | None = None
        while time.time() - t0 < 60:
            if self._proc.poll() is not None:
                raise RuntimeError("postgres terminó durante el arranque.")
            try:
                self._conn = self._psycopg.connect(self.dsn("postgres"), autocommit=True, connect_timeout=2)
                self._conn.close()
                self._conn = None
                return
            except Exception as exc:
                ultimo_error = exc
                time.sleep(0.5)
        raise RuntimeError(f"postgres no aceptó conexiones: {ultimo_error}")

    def _crear_bd_sesion(self) -> None:
        conn = self._psycopg.connect(self.dsn("postgres"), autocommit=True)
        try:
            conn.execute(f'DROP DATABASE IF EXISTS "{self.dbname}"')
            conn.execute(f'CREATE DATABASE "{self.dbname}"')
        finally:
            conn.close()
        self._conn = self._psycopg.connect(self.dsn(), autocommit=True)

    def close(self) -> None:
        """DROP de la BD de sesión + stop del servidor (tolerante)."""
        if self._conn is not None:
            try:
                self._conn.close()
            except Exception:
                pass
            self._conn = None
        self.tables = {}
        try:
            if self._proc is not None and self._proc.poll() is None:
                admin = self._psycopg.connect(self.dsn("postgres"), autocommit=True, connect_timeout=5)
                try:
                    admin.execute(f'DROP DATABASE IF EXISTS "{self.dbname}"')
                finally:
                    admin.close()
        except Exception:
            pass
        try:
            if self._proc is not None and self._proc.poll() is None:
                self._proc.terminate()
                self._proc.wait(timeout=30)
        except Exception:
            pass
        self._proc = None

    # ------------------------------------------------------------------ datos

    def _limpiar_bd(self) -> None:
        assert self._conn is not None
        for name in list(self.tables):
            try:
                self._conn.execute(f'DROP TABLE IF EXISTS "{name}"')
            except Exception:
                pass
        self.tables = {}

    def load_tables(self, tables: list[Table]) -> list[str]:
        """Sustituye las tablas de la sesión (paridad con SQLEngine)."""
        assert self._conn is not None
        self._limpiar_bd()
        omitidas: list[str] = []
        if not tables:
            return omitidas
        for t in tables:
            if not t.columns:
                omitidas.append(t.name)
                continue
            cols = ", ".join(f'"{c.name}" {_tipo_pg(c.type)}' for c in t.columns)
            try:
                self._conn.execute(f'CREATE TABLE "{t.name}" ({cols})')
            except Exception:
                try:
                    self._conn.rollback()
                except Exception:
                    pass
                omitidas.append(t.name)
                continue
            ncols = len(t.columns)
            vals = ", ".join(["%s"] * ncols)
            lote = []
            for row in t.rows:
                reg = [None] * ncols
                for i, v in enumerate(row[:ncols]):
                    reg[i] = _valor_pg(v)
                lote.append(tuple(reg))
            try:
                cur = self._conn.cursor()
                try:
                    cur.executemany(f'INSERT INTO "{t.name}" VALUES ({vals})', lote)
                finally:
                    cur.close()
            except Exception:
                for reg in lote:  # fallback fila por fila (paridad RG-06)
                    try:
                        self._conn.execute(f'INSERT INTO "{t.name}" VALUES ({vals})', reg)
                    except Exception:
                        continue
            self.tables[t.name] = t
        return omitidas

    def execute(self, query: str) -> QueryResult:
        """Ejecuta una o varias sentencias; devuelve el último resultado con filas."""
        if self._conn is None:
            return QueryResult(ok=False, error="Todavía no hay tablas cargadas. Carga un archivo de ejercicio primero.")
        query = query.strip().strip(";")
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
        assert self._conn is not None
        try:
            cur = self._conn.execute(query)
            try:
                rows = [list(r) for r in cur.fetchall()]
            except Exception:
                rows = []
            columns = [d[0] for d in (cur.description or [])]
            n = len(rows)
            return QueryResult(ok=True, columns=columns, rows=rows, row_count=n,
                               message=f"Consulta ejecutada correctamente. {n} fila(s)")
        except Exception as exc:
            try:
                self._conn.rollback()
            except Exception:
                pass
            return QueryResult(ok=False, error=friendly_error(str(exc), self.tables.keys(), query))

    def exportar_db(self, path: str) -> None:
        """Vuelca la BD de sesión a SQL restorable (vía pg_dump del bundle)."""
        if self._conn is None:
            raise ValueError("No hay tablas cargadas.")
        r = subprocess.run(
            [self._exe("pg_dump.exe"), "-h", "127.0.0.1", "-p", str(self.puerto),
             "-U", self.usuario, "-d", self.dbname, "-f", path],
            capture_output=True, text=True, env=self._env, timeout=300,
        )
        if r.returncode != 0:
            raise OSError(f"pg_dump falló:\n{(r.stdout + r.stderr)[-1000:]}")

    def table_names(self) -> list[str]:
        return list(self.tables.keys())

    def column_names(self, table: str) -> list[str]:
        t = self.tables.get(table)
        return [c.name for c in t.columns] if t else []


__all__ = ["PGEngine", "PG_BIN_DIR", "PG_VERSION", "_tipo_pg"]
