# SPEC: comparar-consultas

## Meta
- **Feature**: comparar-consultas
- **Autor**: opencode (Muse Spark)
- **Fecha**: 2026-09-21
- **Estado**: `APPROVED`

## Objetivo
Comparar dos consultas del **historial de la sesión** (A2 descartado):
ejecutar A y B y mostrar si devuelven lo mismo (filas, columnas, muestra
de diferencias). Caso típico: dos formas de calcular lo mismo.

## Acceptance Criteria

### CP-01 — comparar iguales
- **Given** dos consultas del historial con igual resultado
- **When** `comparar_consultas(qa, qb)`
- **Then** `iguales=True`, mismos conteos; sin crash.

### CP-02 — comparar distintas
- **Given** resultados distintos (filas o columnas)
- **When** comparar
- **Then** `iguales=False` + resumen (`FILAS: a vs b`, `COLUMNAS: ...`) + muestra de hasta 5 filas de diferencia.

### CP-03 — diálogo desde historial
- **Given** historial con ≥2 entradas
- **When** clic `COMPARAR` (en la barra del historial)
- **Then** diálogo con dos listas (A/B) + botón comparar; el veredicto va al toast y a un diálogo de resultado; con <2 entradas, toast `SE NECESITAN 2 CONSULTAS`.

### CP-04 — errores
- **Given** alguna consulta falla al re-ejecutar
- **When** comparar
- **Then** el error se reporta (`ERROR EN A/B: ...`), sin crash.

## Edge Cases
- [x] Misma consulta dos veces → iguales.
- [x] Orden de filas distinto: se comparan como multisets (orden-insensible) + aviso si solo difiere el orden.
- [x] `None` en filas: comparable (tupla con None es hasheable).

## Límites Conocidos
- Solo historial de la sesión (A2 descartado: sin persistencia).
- Muestra de diff topada en 5 filas.

## Archivos a tocar
- `core/sqlite_engine.py` o helper en `ui/` (`comparar_consultas(qa, qb)` puro, testeable sin Qt)
- `ui/main_window.py` + `ui/paneles.py` (botón COMPARAR + diálogo)
- `tests/test_comparar_consultas.py` (nuevo: CP-01..CP-04)

## Tests requeridos
- **Unit**: comparar puro (iguales, distintas filas/columnas, orden, errores).
- **E2E**: botón, diálogo con <2 (toast), veredicto iguales.
- **Nombre de archivos de test**: `tests/test_comparar_consultas.py`

## Notas de diseño
- Lógica pura en `core/comparar.py` (nuevo, sin Qt): `(qa, qb, engine) -> dict`; UI solo presenta.
- Multiset vía `Counter(map(tuple))`; filas como tuplas (None ok; listas no hasheables → tupla).
