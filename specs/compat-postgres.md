# SPEC: compat-postgres

## Meta
- **Feature**: compat-postgres
- **Autor**: opencode (Muse Spark)
- **Fecha**: 2026-09-18
- **Estado**: `APPROVED`

## Objetivo
El usuario viene de PostgreSQL y choca con el dialecto SQLite (`date_part`,
`::`, `USING` calificado...). Dos medidas: (1) reescribir `expr::TIPO` a
`CAST(expr AS TIPO)` automáticamente; (2) pistas amables cuando el error
huele a postgres-ismo. `CAST` y `USING` simple ya funcionan (regresión).

## Acceptance Criteria

### PG-01 — operador `::`
- **Given** `SELECT '5'::INTEGER + 1`, `"col"::TEXT`, `(a+b)::REAL`
- **When** ejecutar
- **Then** funciona como `CAST(... AS ...)` (124, texto, real).

### PG-02 — literales intactos
- **Given** `'a::b'`, `"x::y"`, comentarios `-- a::b` / `/* a::b */`
- **When** ejecutar
- **Then** no se reescriben (siguen siendo texto/comentario).

### PG-03 — hints de dialecto
- **Given** error al ejecutar consulta con `date_part(` / `extract(` / `now()` / `ILIKE` / `USING t.col`
- **When** se traduce el error
- **Then** el mensaje sugiere la forma SQLite (`STRFTIME`, `DATE('now')`, `LIKE`, `USING (col)` sin tabla).

### PG-04 — regresión CAST/USING
- **Given** `CAST('123' AS INTEGER)`, `JOIN ... USING(id)`
- **When** ejecutar
- **Then** ok (ya funcionaban; queda fijado por tests).

## Edge Cases
- [x] `::` anidados (`(a)::TEXT::VARCHAR`): reescritura iterada.
- [x] Tipos con parámetros (`VARCHAR(10)`): se preservan.
- [x] `::` sin operando válido: se deja tal cual (SQLite dará su error).
- [x] `friendly_error` sin query (llamadas viejas): comportamiento intacto.

## Límites Conocidos
- Operandos complejos con paréntesis anidados (`(f(a))::TEXT`): usar `CAST` explícito.
- No es Postgres: `GENERATE_SERIES`, `RETURNING` en ciertos contextos, `ILIKE` binario, etc. siguen sin existir; el hint lo explica.
- SQLite documenta su dialecto; la app no pretende paridad total.

## Archivos a tocar
- `core/sqlite_engine.py` (`_reescribir_cast_postgres`, aplicar en `execute`)
- `core/error_friendly.py` (`_SUGERENCIAS_DIALECTO` + param `query` opcional)
- `tests/test_compat_postgres.py` (nuevo: PG-01..PG-04)

## Tests requeridos
- **Unit**: rewrite directo; hints por query; regresión CAST/USING e2e.
- **Nombre de archivos de test**: `tests/test_compat_postgres.py`

## Notas de diseño
- La reescritura respeta literales/comentarios (segmentación como `_partir_sentencias`).
- `friendly_error(raw, tables, query="")`: param opcional, compat con llamadas viejas.
