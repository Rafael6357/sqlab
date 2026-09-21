# SPEC: autocompletar-parentesis

## Meta
- **Feature**: autocompletar-parentesis
- **Autor**: opencode (Muse Spark)
- **Fecha**: 2026-09-18
- **Estado**: `APPROVED`

## Objetivo
El autocompletado cierra paréntesis: completar una función inserta `FUNC()`
con el cursor dentro, y escribir `(` a mano autoinserta el `)` de cierre.

## Acceptance Criteria

### PR-01 — función completada con paréntesis
- **Given** prefijo `COU` + popup con `COUNT`
- **When** se acepta (Enter/Tab/clic)
- **Then** el editor dice `COUNT()` con el cursor entre los paréntesis.

### PR-02 — no-funciones intactas
- **Given** completar `clientes`, `SELECT`, etc.
- **When** se acepta
- **Then** se inserta el texto tal cual, sin paréntesis.

### PR-03 — `(` manual se autocierra
- **Given** editor sin popup visible
- **When** se escribe `(`
- **Then** se inserta `()` con el cursor dentro (cada `(` suma su propio par).

## Edge Cases
- [x] Funciones en minúsculas (`count`): se respeta lo escrito + `()`.
- [x] `(` con texto seleccionado: se envuelve la selección entre paréntesis.
- [x] `(` con popup visible: se escribe normal (el popup re-filtra), sin autocierre.

## Límites Conocidos
- Set fijo de funciones: `COUNT SUM AVG MIN MAX ROUND LENGTH COALESCE` (las de `SQL_KEYWORDS` con paréntesis).
- Sin resaltado de pares ni salto sobre `)` existente (fuera de alcance).

## Archivos a tocar
- `ui/main_window.py` (`_insert_completion`, `eventFilter`)
- `tests/test_autocompletar_parentesis.py` (nuevo: PR-01..PR-03)

## Tests requeridos
- **Unit/E2E**: texto + posición de cursor tras completar función; no-función intacta; `(` manual → `()` + cursor dentro; con popup → normal.
- **Nombre de archivos de test**: `tests/test_autocompletar_parentesis.py`

## Notas de diseño
- Cursor: `tc.position()` debe quedar justo tras `(` de apertura.
