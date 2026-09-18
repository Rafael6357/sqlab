# SPEC: mostrar-null-en-grillas

## Meta
- **Feature**: mostrar-null-en-grillas
- **Autor**: opencode (Muse Spark)
- **Fecha**: 2026-09-17
- **Estado**: `APPROVED`

## Objetivo
Las celdas con valor `None` (nulo real) deben mostrar el texto `NULL` con estilo
tenue en las grillas, en vez de verse vacías e indistinguibles de `""`.
Aplica al visor (`CONTENIDO DE LA TABLA`) y al resultado
(`RESULTADO DE LA CONSULTA`), y al fichero del `EXPORTAR CSV`.

## Acceptance Criteria

### NL-01 — visor muestra NULL tenue
- **Given** una tabla con celdas `None`
- **When** se pinta en el visor
- **Then** la celda dice `NULL`, tooltip `NULL`, color `#4d7c6d` (tenue del tema) + cursiva, sin alineación numérica.

### NL-02 — resultado muestra NULL tenue
- **Given** un resultado con celdas `None`
- **When** se pinta en `RESULTADO DE LA CONSULTA`
- **Then** igual que NL-01.

### NL-03 — cadena vacía sigue vacía
- **Given** una celda con `""`
- **When** se pinta
- **Then** celda vacía, sin tooltip, indistinguible de hoy (se distingue de `NULL`).

### NL-04 — escalares intactos
- **Given** `0`, `0.0`, `False`, strings normales
- **When** se pintan
- **Then** texto tal cual; `int`/`float` mantienen alineación derecha.

### NL-05 — anchos miden el literal
- **Given** columna con `None`
- **When** `_ajustar_anchos` mide la muestra
- **Then** usa el ancho de `"NULL"` (no deja la columna estrecha).

### NL-06 — export CSV escribe NULL (enmienda a EX-03)
- **Given** valores `None` en el último resultado
- **When** exportar
- **Then** el fichero trae `NULL` (sin entrecomillar); BOM `utf-8-sig` y `QUOTE_MINIMAL` intactos.

## Edge Cases
- [x] Celda vacía `""` vs `None`: distinguibles.
- [x] String literal `"NULL"`: mismo texto visible (limitación conocida; solo el estilo tenue delata al nulo real).
- [x] `None` en cabeceras: no aplica (cabeceras siempre `str`).
- [x] Tablas grandes: sin costo extra (un `setForeground`/`setFont` por celda nula).

## Límites Conocidos
- Los `None` siguen siendo nulos reales en motor/carga/sesión (JSON `null` al guardar/cargar); solo cambia la representación visual y el CSV.
- El color por ítem puede verse afectado por el QSS en algunos estilos; los tests asertan texto/tooltip/fuente (funcional) y el color se verifica visualmente.
- Enmienda a spec `exportar-resultado-csv` EX-03: `None`→`NULL` (antes vacío). Test EX-03 reescrito.

## Archivos a tocar
- `specs/exportar-resultado-csv.md` (enmienda EX-03)
- `tests/test_mostrar_null.py` (nuevo: NL-01..NL-05)
- `tests/test_exportar_csv.py` (reescribir EX-03: NL-06)
- `ui/tablas.py` (`_item_grilla`, `_ajustar_anchos`)
- `ui/main_window.py` (`exportar_resultado_csv`, línea del writer)

## Tests requeridos
- **Unit**: `_item_grilla(None)` → texto/tooltip/fuente/alineación; `_ajustar_anchos` con `None`.
- **E2E**: visor y resultado pintan `NULL`; export escribe `NULL`.
- **Nombre de archivos de test**: `tests/test_mostrar_null.py`

## Notas de diseño
- Punto único de control: `_item_grilla` (visor y resultado delegan ahí).
- Color `#4d7c6d` = tenue oficial del tema (`MutedLabel`/`StatusLabel` en `dark.qss`).
- Alternativa descartada: dejar export con vacío (el usuario pidió `NULL` también en CSV para analizar fuera de la app sin ambigüedad).
