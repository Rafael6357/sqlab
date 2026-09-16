# SPEC: fix-matriz-resultados — Matriz nunca tapa el editor

- **Feature**: Fix splitter matriz/editor no colapsable y siempre recuperable
- **Autor**: agente
- **Fecha**: 2026-09-16
- **Estado**: APPROVED

## Objetivo
Evitar que la `>> MATRIZ DE RESULTADOS` pueda expandirse hasta tapar por completo el editor SQL y dejar la consola en estado roto sin handle para volver.

## Acceptance Criteria

### MR-01: Editor y matriz nunca colapsan a 0
- **Given** ventana principal abierta (tamaño por defecto 1360×840)
- **When** el usuario arrastra el divisor del `QSplitter` horizontal (editor `|` matriz) completamente hacia la izquierda o derecha
- **Then** editor mantiene `≥220px` y matriz `≥240px`; el handle queda siempre visible y arrastrable

### MR-02: Reseteo por doble-clic
- **Given** divisor en cualquier posición desplazada
- **When** doble-clic sobre el handle
- **Then** los tamaños vuelven a `~50/50` (`setSizes([w//2, w//2])`)

### MR-03: Redimensionado de ventana pequeño
- **Given** ventana redimensionada a ancho mínimo del sistema
- **When** se recalcula el layout
- **Then** ningún panel colapsa a `0`; ambos respetan sus mínimos

## Edge Cases
- [ ] Ventana 1024px de ancho (portátil): 220+240+290(LefPanel) cabe, splitter reparte sin overflow
- [ ] Arrastrar muy rápido al borde + soltar
- [ ] Abrir app, no tocar divisor, tamaños iniciales 500/500 se respetan
- [ ] Doble-clic repetido no crashea

## Límites Conocidos
- Sin botón extra de reset (solo doble-clic); sin persistencia de posición del divisor entre sesiones
- La estética se mantiene oscura 1px visual; el hit-area real es 6px (padding transparente) para usabilidad

## Archivos a tocar
- `ui/main_window.py` (`_build_editor_pane`, `_build_output_pane`, `_build_workspace`)
- `resources/dark.qss` (`QSplitter::handle`)
- Tests E2E Qt offscreen

## Tests requeridos
- **Unit/E2E**: `tests/test_fix_matriz.py` (o ampliar `test_e2e_smoke.py`)
  - `test_matriz_splitter_no_colapsable` — `isCollapsible(0)==False and isCollapsible(1)==False`
  - `test_matriz_minimum_widths` — `editor.minimumWidth()>=220`, `output.minimumWidth()>=240`
  - `test_matriz_handle_recuperable` — `setSizes([0,1000])` luego `editor.width()>=220` y `output.width()>=240` tras clamp
  - `test_matriz_handle_width` — `handleWidth()>=4`
- **Nombre de archivos de test**: `tests/test_fix_matriz.py`

## Notas de diseño
- `QSplitter.setChildrenCollapsible(False)` evita colapso a 0 por drag. Mínimos garantizan handle siempre en viewport.
- `setHandleWidth(6)` da área de agarre usable; `dark.qss` pinta solo 1px (+ `margin:0 2px`) para look fino.
