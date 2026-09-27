# SPEC: error-friendly-pg (F2)

## Meta
- **Feature**: error-friendly-pg
- **Autor**: opencode (Muse Spark)
- **Fecha**: 2026-09-27
- **Estado**: `APPROVED`

## Objetivo
`friendly_pg_error()` traduce errores PostgreSQL a español principiante
(igual tono que `friendly_error` de SQLite): por SQLSTATE cuando viene del
servidor real, con fallback a regex del mensaje (testeable sin servidor).
Los hints de dialecto SQLite (`::`→CAST, `date_part`→STRFTIME) NO aplican
en PG y no deben dispararse.

## Acceptance Criteria

### FE-01 — tabla/columna inexistente
- **Given** `42P01 relation "x" does not exist` / `42703 column "y" does not exist`
- **When** traducir
- **Then** `No existe la tabla «x». ...` / `No existe la columna «y». ...` en español.

### FE-02 — sintaxis y función
- **Given** `42601 syntax error at or near "SEL"` / `42883 function date_part(unknown, integer) does not exist`
- **When** traducir
- **Then** mensaje de sintaxis con el token + sugerencia SQLite→PG invertida cuando aplique (p. ej. nada que sugerir: `date_part` existe; el problema son los tipos → hint de tipos).

### FE-03 — sin SQLSTATE (fallback texto)
- **Given** solo texto de error PG (sin conexión)
- **When** traducir
- **Then** mismos mensajes vía regex; desconocido → genérico con texto recortado.

### FE-04 — cableado
- **Given** `PGEngine._ejecutar_una` con error real
- **When** falla
- **Then** usa `friendly_pg_error` con `sqlstate` de la excepción (los tests e2e lo verifican contra servidor; unitarios sin servidor).

## Edge Cases
- [x] `friendly_error` de SQLite intacto (14 tests existentes).
- [x] Excepción sin `sqlstate` (corte de conexión `08006`, etc.): genérico + texto.
- [x] Nombres entrecomillados con espacios: regex tolerante.

## Límites Conocidos
- Cubre los SQLSTATE comunes (42P01, 42703, 42601, 42883, 42P02, 22P02, 23505, 23503); el resto va al genérico.
- UI (F4) mostrará estos mensajes sin cambios de widgets.

## Archivos a tocar
- `core/error_friendly.py` (`friendly_pg_error` + `_PATRONES_PG`)
- `core/pg_engine.py` (usar `friendly_pg_error` con sqlstate)
- `tests/test_error_friendly_pg.py` (nuevo: FE-01..FE-04)

## Tests requeridos
- **Unit**: strings PG reales → español (sin servidor).
- **E2E**: errores reales contra servidor (skip sin binarios).
- **Nombre de archivos de test**: `tests/test_error_friendly_pg.py`

## Notas de diseño
- Firma: `friendly_pg_error(raw, table_names=(), query="", sqlstate=None)`.
- `psycopg` expone `exc.sqlstate`; el engine lo pasa explícito (testeable).
