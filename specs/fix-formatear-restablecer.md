# SPEC: Fix críticos — formatear_consulta y restablecer_datos

> Feature ID: `fix-formatear-restablecer`

## Meta
- **Feature**: Corrección de dos bugs críticos de la ventana principal (C1 y C2 del audit UI)
- **Autor**: audit (ai)
- **Fecha**: 2026-09-15
- **Estado**: `IMPLEMENTADO`

## Objetivo
1. `restablecer_datos()` debe recargar el preset original (`ejemplo_tienda.json`) y no quedarse como no-op que solo re-lista el estado actual mutado.
2. `formatear_consulta()` debe formatear SOLO keywords fuera de literales de texto y comentarios, preservando la semántica de la consulta.

## Acceptance Criteria

### C1-01 — restablecer_datos recarga el preset original de arranque
- **Given** la app arrancó con `ejemplo_tienda.json` (tablas `clientes`, `pedidos`)
- **When** se llama a `restablecer_datos()`
- **Then** `engine.table_names()` incluye `clientes` y `pedidos`, `tabla_list.count() >= 2`, `tables_count.text()` coincide con el conteo real

### C1-02 — restablecer_datos revierte el estado tras cargar otro ejercicio
- **Given** se cargó `ejemplo_biblioteca.json` (tablas `libros`, `usuarios`, `prestamos`)
- **When** se llama a `restablecer_datos()`
- **Then** las tablas vuelven a incluir `clientes` y `pedidos` (preset de arranque)

### C1-03 — restablecer_datos respeta el historial y limpia el editor de resultados
- **Given** hay consultas en el historial y el resultado visible
- **When** se llama a `restablecer_datos()`
- **Then** el historial se conserva, `resultado_tabla` no queda visible con datos de la sesión anterior y el editor restaura el default del preset

### C2-01 — keywords fuera de literales se formatean a mayúsculas
- **Given** el editor contiene `select * from clientes`
- **When** se llama a `formatear_consulta()`
- **Then** el editor contiene `SELECT` y `FROM` en mayúsculas (comportamiento SC-09 del spec ui-main-window, sin regresión)

### C2-02 — literal de texto simple no se altera
- **Given** el editor contiene `select * from clientes where nombre = 'from spain'`
- **When** se llama a `formatear_consulta()`
- **Then** el contenido dentro de `'...'` sigue siendo `from spain` en minúsculas (no `FROM SPAIN`)

### C2-03 — literal con comilla escapada ('' SQLite) no se altera y no rompe el parser
- **Given** el editor contiene `select nombre from clientes where nombre like 'it''s from'`
- **When** se llama a `formatear_consulta()`
- **Then** el output sigue siendo una única cadena válida (`it''s from` preservado) y los keywords circundantes están en mayúsculas

### C2-04 — comentario de línea (`--`) se preserva intacto
- **Given** el editor contiene `select * from clientes -- select secreto`
- **When** se llama a `formatear_consulta()`
- **Then** el comentario no contiene `SELECT` en mayúsculas; se preserva `-- select secreto` y el `SELECT` real sí se formatea

### C2-05 — comentario de bloque (`/* */`) se preserva intacto
- **Given** el editor contiene `select * from clientes /* where x */`
- **When** se llama a `formatear_consulta()`
- **Then** el contenido `where x` dentro del bloque se preserva en minúsculas y `SELECT`/`FROM` se formatean

### C2-06 — editor vacío no crashea
- **Given** el editor está vacío
- **When** se llama a `formatear_consulta()`
- **Then** no hay excepción y el editor permanece vacío (edge case del spec ui-main-window)

## Edge Cases
- [x] Editor vacío → sin crash (C2-06)
- [x] Literal con `''` escapada dentro del string → no rompe (C2-03)
- [x] Comentario de línea y de bloque al inicio/mitad/final → preservados (C2-04, C2-05)
- [ ] String que contiene carácter de comilla simple dentro de comentario de línea → se preserva
- [ ] `restablecer_datos` con preset de arranque ausente (no existe fixture) → cae en estado sin tablas sin crash

## Límites Conocidos
- `restablecer_datos()` siempre apunta al preset de arranque por defecto (`ejemplo_tienda.json`); si el usuario arrancó la app en una carpeta sin ese archivo, el reset no tiene preset que recargar (comportamiento de boot actual, no cambia).
- El formateo no normaliza espacios/indentación; solo MAYÚSCULAS de keywords. No es un SQL beautifier completo.
- Las comillas dobles (`"..."`) en SQLite pueden representar identificadores; el formateador NO tocará su contenido (tratadas como literal protegido, consistente con el comportamiento seguro).

## Archivos a tocar
- `app-sql-offline/ui/main_window.py` — método `restablecer_datos()` (aprox. línea 1001) y `formatear_consulta()` (aprox. línea 976)
- `app-sql-offline/tests/test_e2e_smoke.py` — tests nuevos para ambos fixes

## Tests requeridos
- **E2E (test_e2e_smoke.py)**: C1-01, C1-02, C2-01..C2-06 como tests Qt offscreen usando el fixture `app`
- **Unit**: estrategia de formateo puede testearse como helper puro si se extrae (opcional); se valida vía E2E sobre el editor

## Notas de diseño
- Para `formatear_consulta` se recomienda un único pasadizo por caracteres (state machine) que distingue `'...'`, `"..."`, `-- comentario`, `/* ... */` y aplica `upper()` solo fuera de esos contextos. Esto evita el bug actual con `re.sub(rf"\b{kw}\b", ...)` global.
- Para `restablecer_datos`: reutilizar `cargar_preset("ejemplo_tienda.json", silencioso=True)` (mismo mecanismo que `_load_initial_preset`) en lugar de solo refrescar la vista.
- No tocar `resources/dark.qss`, ni `core/sqlite_engine.py`, ni `core/session_loader.py` (fuera de alcance de estos fixes).