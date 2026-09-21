"""Compara dos consultas sobre el mismo engine (spec comparar-consultas).

Lógica pura sin Qt: ejecuta A y B y devuelve un veredicto. Las filas se
comparan como multisets (orden-insensible); si solo difiere el orden se
avisa.
"""
from __future__ import annotations

from collections import Counter
from typing import Any


def comparar_consultas(qa: str, qb: str, engine) -> dict[str, Any]:
    """Ejecuta qa y qb y compara. Claves: iguales, solo_orden, resumen, diff, error."""
    ra = engine.execute(qa)
    if not ra.ok:
        return {"iguales": False, "solo_orden": False, "resumen": f"ERROR EN A: {ra.error}", "diff": [], "error": ra.error}
    rb = engine.execute(qb)
    if not rb.ok:
        return {"iguales": False, "solo_orden": False, "resumen": f"ERROR EN B: {rb.error}", "diff": [], "error": rb.error}
    if list(ra.columns) != list(rb.columns):
        return {
            "iguales": False,
            "solo_orden": False,
            "resumen": f"COLUMNAS DISTINTAS: {list(ra.columns)} vs {list(rb.columns)}",
            "diff": [],
            "error": "",
        }
    fa = [tuple(r) for r in ra.rows]
    fb = [tuple(r) for r in rb.rows]
    if fa == fb:
        return {"iguales": True, "solo_orden": False, "resumen": f"IGUALES: {len(fa)} FILAS", "diff": [], "error": ""}
    if Counter(fa) == Counter(fb):
        return {
            "iguales": False,
            "solo_orden": True,
            "resumen": f"SAME FILAS ({len(fa)}), DISTINTO ORDEN — agrega ORDER BY para comparar",
            "diff": [],
            "error": "",
        }
    ca, cb = Counter(fa), Counter(fb)
    solo_a = list((ca - cb).elements())[:5]
    solo_b = list((cb - ca).elements())[:5]
    diff = [("SOLO EN A", list(r)) for r in solo_a] + [("SOLO EN B", list(r)) for r in solo_b]
    return {
        "iguales": False,
        "solo_orden": False,
        "resumen": f"FILAS: {len(fa)} vs {len(fb)}",
        "diff": diff,
        "error": "",
    }
