# SPEC: autocompletar-con-enter

## Meta
- **Feature**: autocompletar-con-enter
- **Autor**: opencode (Muse Spark)
- **Fecha**: 2026-09-18
- **Estado**: `APPROVED`

## Objetivo
Aceptar la sugerencia del autocompletado con **Enter** o **Tab**, no solo con
clic: hoy el popup no garantiza ítem resaltado ni filtra las teclas, y Enter
cae al editor como salto de línea.

## Acceptance Criteria

### AC-01 — Enter inserta
- **Given** popup visible con sugerencias y AUTOCOMPLETAR activo
- **When** Enter/Return
- **Then** se inserta la resaltada (o la primera) reemplazando el prefijo; no se inserta salto de línea.

### AC-02 — Tab inserta
- **Given** popup visible
- **When** Tab
- **Then** igual que AC-01 (no cambia el foco; el editor ya tiene `setTabChangesFocus(False)`).

### AC-03 — atajos intactos
- **Given** popup visible u oculto
- **When** Ctrl+Enter / F5
- **Then** se ejecuta la consulta (nunca inserta); Escape cierra el popup sin insertar ni cambiar texto.

### AC-04 — sin popup no cambia nada
- **Given** popup oculto o AUTOCOMPLETAR apagado
- **When** Enter/Tab
- **Then** comportamiento actual (salto de línea / tabulación).

## Edge Cases
- [x] Prefijo a mitad de palabra: se reemplaza solo la palabra bajo el cursor (lógica actual de `_insert_completion`).
- [x] Popup visible pero sin coincidencia: Enter hace salto de línea (no hay nada que aceptar).
- [x] `activated` por clic sigue funcionando (no se duplica la inserción: al aceptar por tecla se oculta el popup).

## Límites Conocidos
- Solo `QCompleter` en `PopupCompletion` del editor SQL; no hay navegación adicional (arriba/abajo ya la maneja Qt).

## Archivos a tocar
- `ui/main_window.py` (extender `eventFilter` + auto-resaltado tras `complete()`)
- `tests/test_autocompletar_enter.py` (nuevo: AC-01..AC-04 con `qtbot.keyClick`)

## Tests requeridos
- **Unit/E2E**: prefijo + Enter → texto insertado; Tab igual; Ctrl+Enter → ejecuta; Escape → cierra sin cambios; popup oculto → Enter normal.
- **Nombre de archivos de test**: `tests/test_autocompletar_enter.py`

## Notas de diseño
- Reutiliza el `eventFilter` existente (hoy filtra el splitter): si el popup del completer está visible y la tecla es Enter/Return/Tab, se acepta y se consume el evento (`return True`).
- Tras `complete()` se fija la fila actual en 0 para garantizar resaltado.
