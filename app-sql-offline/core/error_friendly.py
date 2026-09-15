"""Traduce errores de SQLite a mensajes entendibles para un principiante."""
from __future__ import annotations

import re
from collections.abc import Iterable

_PATTERNS: list[tuple[str, str]] = [
    (r"no such table:\s*([\w\"]+)", "No existe la tabla \u00ab{0}\u00bb. Revisa la lista de tablas del panel izquierdo."),
    (r"no such column:\s*([\w\"]+)", "No existe la columna \u00ab{0}\u00bb. Revisa los nombres de las columnas de la tabla que est\u00e1s usando."),
    (r"ambiguous column name:\s*([\w\"]+)", "La columna \u00ab{0}\u00bb existe en m\u00e1s de una tabla. Prefija el nombre con la tabla: tabla.{0}."),
    (r"near\s*\"?([\w]+)\"?:\s*syntax error", "Error de sintaxis cerca de \u00ab{0}\u00bb. Revisa la ortograf\u00eda del SQL, los espacios y las comas."),
    (r"syntax error (?:near \"?([\w\"',;)]*)\"?)?", "Error de sintaxis cerca de \u00ab{0}\u00bb. Revisa la ortograf\u00eda del SQL, los espacios y las comas."),
    (r"incomplete input", "La consulta est\u00e1 incompleta. Rev\u00edsala; suele faltar un valor, un par\u00e9ntesis o un cierre de cadena."),
    (r"no such function:\s*([\w\"]+)", "No existe la funci\u00f3n \u00ab{0}\u00bb. Ejemplos v\u00e1lidos: COUNT, SUM, AVG, MIN, MAX."),
    (r"unknown column(.{0,40})", "Referencia a una columna desconocida:{0}."),
    (r"table .* has (?:no column named|no such column)\s*([\w\"]+)", "La tabla no tiene una columna llamada \u00ab{0}\u00bb."),
    (r"datatype mismatch", "Los tipos de datos no coinciden. Probablemente est\u00e1s mezclando texto (TEXT) con n\u00fameros (INTEGER/REAL)."),
    (r"foreign key constraint failed", "La fila que intentas insertar viola una llave for\u00e1nea."),
    (r"constraint failed", "Se viol\u00f3 una restricci\u00f3n de la base de datos (campo \u00fanico o no nulo)."),
    (r"unable to open database file", "No se pudo abrir la base de datos."),
    (r"unsupported file format", "Formato de archivo no soportado."),
]


def _quote_error(raw: str) -> str:
    return raw.replace("\n", " ")[:220]


def friendly_error(raw: str, table_names: Iterable[str] = ()) -> str:
    low = raw.lower()
    for pattern, template in _PATTERNS:
        m = re.search(pattern, low)
        if not m:
            continue
        try:
            ident = m.group(1).strip().strip('"') if m.lastindex else raw.strip()
        except IndexError:
            ident = raw.strip()
        msg = template.format(ident)
        if "syntax error" in pattern and not m.lastindex:
            msg = "Error de sintaxis. Revisa la consulta."
        return msg
    return f"La base de datos respondi\u00f3 con un error:\n{_quote_error(raw)}"