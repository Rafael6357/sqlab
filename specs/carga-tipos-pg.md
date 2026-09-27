# SPEC: carga-tipos-pg (F3)

## Meta
- **Feature**: carga-tipos-pg
- **Autor**: opencode (Muse Spark)
- **Fecha**: 2026-09-27
- **Estado**: `APPROVED`

## Objetivo
El loader infiere y convierte tipos PostgreSQL: `BOOLEAN` (textos
true/false/yes/no → `bool` real, porque PG rechaza `'true'`::text en columna
BOOLEAN), `DATE` (`AAAA-MM-DD`) y `TIMESTAMP` (`AAAA-MM-DD HH:MM:SS`, PG
acepta el ISO como texto). JSON respeta strings explícitos salvo booleanos
declarados. `_VALID_TYPES` suma `TIMESTAMP`.

## Acceptance Criteria

### CT-01 — inferencia
- **Given** columna CSV con `true/TRUE/False`, `2024-05-01`, `2024-05-01 10:00:00`
- **When** inferir
- **Then** `BOOLEAN`, `DATE`, `TIMESTAMP`; `"t"`/`"f"` sueltas NO son boolean (riesgo iniciales); `"2024-13-45"` es `TEXT`.

### CT-02 — conversión bool
- **Given** columna inferida/declarada `BOOLEAN` con strings
- **When** cargar (CSV/JSON)
- **Then** valores `True`/`False` Python; `None` intacto. Excel ya trae bool nativo.

### CT-03 — e2e PG
- **Given** CSV con bool + fecha
- **When** `load_tables` en `PGEngine` + `SELECT` con filtro bool y comparación de fecha
- **Then** filas correctas, tipos PG reales (skip sin binarios).

## Edge Cases
- [x] Mezcla bool+texto → TEXT (sin conversión).
- [x] `_infer_type("NULL")` sigue `TEXT` (tests viejos intactos).
- [x] JSON con `"tipo": "BOOLEAN"` y `"NA"` → `None` (nulidad manda).

## Límites Conocidos
- Fechas no-ISO quedan `TEXT` (PG las compara como texto).
- `TIME`/`VARCHAR(n)` no se infieren (sí se respetan declarados).

## Archivos a tocar
- `core/session_loader.py` (`_infer_type`, conversión en `_parse_csv`/`_parse_json`, `_VALID_TYPES`)
- `tests/test_carga_tipos_pg.py` (nuevo: CT-01..CT-03)

## Tests requeridos
- **Unit**: inferencia + conversión por formato.
- **E2E**: CSV → PGEngine → filtros (skip sin binarios).
- **Nombre de archivos de test**: `tests/test_carga_tipos_pg.py`

## Notas de diseño
- Sin conversión, PG aborta el INSERT (`invalid input syntax for type boolean`); por eso el bool es real y la fecha puede quedar ISO-texto.
