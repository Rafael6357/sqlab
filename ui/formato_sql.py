"""Formateador SQL real de SQLab (spec formato-sql-real).

Keywords en MAYÚSCULAS + salto de línea antes de cada cláusula + indentación
(2 espacios/nivel, subconsultas +1). Protege literales '...'/"..." y
comentarios -- y /* */ (byte por byte). Sin dependencias externas. Idempotente.
"""
from __future__ import annotations


SQL_KEYWORDS = [
    "SELECT", "FROM", "WHERE", "GROUP", "BY", "ORDER", "HAVING", "LIMIT",
    "INSERT", "INTO", "VALUES", "UPDATE", "SET", "DELETE", "CREATE", "TABLE",
    "JOIN", "INNER", "LEFT", "RIGHT", "ON", "AS", "AND", "OR", "NOT", "NULL",
    "IS", "IN", "LIKE", "BETWEEN", "DISTINCT", "UNION", "ALL", "COUNT", "SUM",
    "AVG", "MIN", "MAX", "ROUND", "LENGTH", "COALESCE",
    "CASE", "WHEN", "THEN", "ELSE", "END", "PRIMARY", "KEY", "FOREIGN",
    "REFERENCES", "UNIQUE", "CHECK", "DEFAULT", "DESC", "ASC", "USING",
    "WITH", "OFFSET", "FULL", "CROSS", "OUTER", "NATURAL",
]

_SQL_KEYWORDS_SET = frozenset(SQL_KEYWORDS)

# --- Formateador SQL real (spec formato-sql-real) ---
_COMPUESTAS = {
    ("GROUP", "BY"), ("ORDER", "BY"), ("UNION", "ALL"),
    ("INSERT", "INTO"), ("LEFT", "JOIN"), ("LEFT", "OUTER"),
    ("RIGHT", "JOIN"), ("RIGHT", "OUTER"), ("INNER", "JOIN"),
    ("FULL", "JOIN"), ("FULL", "OUTER"), ("CROSS", "JOIN"),
    ("OUTER", "JOIN"), ("NATURAL", "JOIN"),
}

_CLAUSULAS = {
    "SELECT", "FROM", "WHERE", "GROUP BY", "HAVING", "ORDER BY",
    "LIMIT", "OFFSET", "UNION", "UNION ALL", "VALUES", "INSERT",
    "INSERT INTO", "UPDATE", "DELETE", "CREATE", "SET",
}

_JOINS = {
    "JOIN", "INNER JOIN", "LEFT JOIN", "LEFT OUTER JOIN",
    "RIGHT JOIN", "RIGHT OUTER JOIN", "FULL JOIN", "FULL OUTER JOIN",
    "CROSS JOIN", "NATURAL JOIN",
}

_SUBCLAUSULAS = {"AND", "OR", "ON"}

_OP_COMP = {"=", "<>", "!=", "<=", ">=", "<", ">"}


def _formatear_sql(sql: str) -> str:
    """Formato SQL estándar: keywords en MAYÚSCULAS + salto de línea antes de
    cada cláusula + indentación (2 espacios/nivel, subconsultas +1).

    Protege literales '...'/\"...\" y comentarios -- y /* */ (byte por byte).
    Sin dependencias externas. Idempotente.
    """
    tokens = _tokenizar_sql(sql)
    if not tokens:
        return ""

    out_lines: list[str] = []
    cur = ""
    nivel = 0
    necesita_espacio = False
    pila_bloques: list[bool] = []
    prev_es_palabra = False

    def _nl(extra: int = 0) -> None:
        nonlocal cur, necesita_espacio
        if cur.strip():
            out_lines.append(cur.rstrip())
        cur = "  " * (nivel + extra)
        necesita_espacio = False

    def _put(texto: str) -> None:
        nonlocal cur, necesita_espacio
        if necesita_espacio and cur and not cur.endswith(" "):
            cur += " "
        cur += texto
        necesita_espacio = True

    def _sig_palabra(idx: int) -> str:
        for t_kind, t_txt in tokens[idx:]:
            if t_kind == "word":
                return t_txt.upper()
        return ""

    i = 0
    n = len(tokens)
    while i < n:
        kind, txt = tokens[i]
        if kind == "word":
            # Fusionar compuestos (GROUP BY, LEFT OUTER JOIN, ...) en cadena máxima
            frase = [txt.upper()]
            j = i + 1
            while j < n and tokens[j][0] == "word" and (frase[-1], tokens[j][1].upper()) in _COMPUESTAS:
                frase.append(tokens[j][1].upper())
                j += 1
            clave = " ".join(frase)
            if clave in _CLAUSULAS or clave in _JOINS:
                if cur.strip():
                    _nl()
                _put(clave)
                i = j
            elif clave in _SUBCLAUSULAS:
                _nl(extra=1)
                _put(clave)
                i = j
            else:
                for w, orig in zip(frase, [tokens[k][1] for k in range(i, j)]):
                    _put(w if w in _SQL_KEYWORDS_SET else orig)
                i = j
            prev_es_palabra = True
        elif kind == "str":
            _put(txt)
            i += 1
            prev_es_palabra = True
        elif kind == "lcom":
            if cur.strip():
                cur += " " + txt
            else:
                cur += txt
            _nl()
            i += 1
            prev_es_palabra = False
        elif kind == "bcom":
            if cur.strip():
                cur += " " + txt
            else:
                cur += txt
            necesita_espacio = True
            i += 1
            prev_es_palabra = False
        else:  # sym
            if txt == "(":
                if _sig_palabra(i + 1) in ("SELECT", "WITH", "VALUES"):
                    _put("(")
                    _nl()
                    nivel += 1
                    pila_bloques.append(True)
                    cur = "  " * nivel
                    necesita_espacio = False
                else:
                    if prev_es_palabra:
                        cur += "("  # llamada a función: sin espacio
                    else:
                        _put("(")
                    necesita_espacio = False
                i += 1
                prev_es_palabra = False
            elif txt == ")":
                if pila_bloques:
                    pila_bloques.pop()
                    nivel = max(0, nivel - 1)
                    _nl()
                    cur += ")"
                else:
                    cur = cur.rstrip() + ")"
                necesita_espacio = True
                i += 1
                prev_es_palabra = False
            elif txt == ",":
                cur = cur.rstrip() + ", "
                necesita_espacio = False
                i += 1
                prev_es_palabra = False
            elif txt == ";":
                cur = cur.rstrip() + ";"
                _nl()
                i += 1
                prev_es_palabra = False
            elif txt == ".":
                cur = cur.rstrip() + "."
                necesita_espacio = False
                i += 1
                prev_es_palabra = False
            elif txt in _OP_COMP:
                cur = cur.rstrip() + f" {txt} "
                necesita_espacio = False
                i += 1
                prev_es_palabra = False
            else:
                _put(txt)
                i += 1
                prev_es_palabra = False
    if cur.strip():
        out_lines.append(cur.rstrip())
    return "\n".join(out_lines)


def _tokenizar_sql(sql: str) -> list[tuple[str, str]]:
    """Tokeniza SQL: word | str | lcom | bcom | sym. Espacios fuera de
    literales/comentarios se descartan (el layout los reconstruye)."""
    toks: list[tuple[str, str]] = []
    i = 0
    n = len(sql)
    while i < n:
        ch = sql[i]
        nxt = sql[i + 1] if i + 1 < n else ""
        if ch.isspace():
            i += 1
        elif ch == "-" and nxt == "-":
            j = sql.find("\n", i)
            toks.append(("lcom", sql[i:] if j == -1 else sql[i:j]))
            i = n if j == -1 else j
        elif ch == "/" and nxt == "*":
            j = sql.find("*/", i + 2)
            end = n if j == -1 else j + 2
            toks.append(("bcom", sql[i:end]))
            i = end
        elif ch == "'":
            j = i + 1
            while j < n:
                if sql[j] == "'":
                    if j + 1 < n and sql[j + 1] == "'":
                        j += 2
                    else:
                        j += 1
                        break
                else:
                    j += 1
            toks.append(("str", sql[i:j]))
            i = j
        elif ch == '"':
            j = i + 1
            while j < n:
                if sql[j] == '"':
                    if j + 1 < n and sql[j + 1] == '"':
                        j += 2
                    else:
                        j += 1
                        break
                else:
                    j += 1
            toks.append(("str", sql[i:j]))
            i = j
        elif ch.isalpha() or ch == "_":
            j = i
            while j < n and (sql[j].isalnum() or sql[j] == "_"):
                j += 1
            palabra = sql[i:j]
            toks.append(("word", palabra.upper() if palabra.upper() in _SQL_KEYWORDS_SET else palabra))
            i = j
        elif ch.isdigit():
            j = i
            while j < n and (sql[j].isdigit() or sql[j] == "."):
                j += 1
            toks.append(("word", sql[i:j]))
            i = j
        elif ch + nxt in ("<=", ">=", "<>", "!="):
            toks.append(("sym", ch + nxt))
            i += 2
        else:
            toks.append(("sym", ch))
            i += 1
    return toks
