# SPEC: scrollbars-visibles

## Meta
- **Feature**: scrollbars-visibles
- **Autor**: opencode (Muse Spark)
- **Fecha**: 2026-09-18
- **Estado**: `APPROVED`

## Objetivo
Los scrollbars de toda la app (visor, resultado, listas, editor) son de 4 px
con handle `#173834` casi invisible sobre fondo `#060b0b`: solo se ven en
hover. Darles brillo y grosor permanentes para que siempre se vean, sin
salirse del tema oscuro.

## Acceptance Criteria

### SB-01 — handle siempre visible
- **Given** cualquier scrollbar (vertical u horizontal)
- **When** sin hover
- **Then** el handle usa verde `dim` (`#00aa70`) con borde redondeado: contrasta con el track oscuro sin necesidad de hover.

### SB-02 — hover con brillo fósforo
- **Given** hover sobre el handle
- **When** el cursor está encima
- **Then** el handle pasa a `#00ffaa` (brillo fósforo del tema).

### SB-03 — grosor usable
- **Given** cualquier scrollbar
- **When** se muestra
- **Then** ancho/alto ≥ 10 px (antes 4 px) y `min-height`/`min-width` del handle ≥ 24 px (intacto).

### SB-04 — sin flechas, sin variante clara
- **Given** el QSS
- **When** se revisa
- **Then** `add-line`/`sub-line` siguen en 0 (sin flechas) y no se introduce ningún color claro fuera de la paleta (`#00ffaa`, `#00aa70`, fondos oscuros).

## Edge Cases
- [x] Tablas anchas con scroll horizontal + vertical simultáneos: ambas reglas cubiertas.
- [x] Listas (`QListWidget`) y editor (`QPlainTextEdit`): heredan `QScrollBar` global, sin reglas por widget.
- [x] El QSS se empaqueta en el exe (`run.spec` datas): requiere rebuild para verse en `dist/`.

## Límites Conocidos
- QSS no anima: el "efecto" es color base brillante + hover fósforo (sin transiciones).
- Solo tema oscuro (prohibido variante clara por AGENTS.md).

## Archivos a tocar
- `resources/dark.qss` (bloque `QScrollBar`, líneas ~325-333)
- `tests/test_scrollbars.py` (nuevo: SB-01..SB-04, asserts sobre el texto del QSS, patrón de `test_crono_mode_checked_verde_en_qss`)

## Tests requeridos
- **Unit**: asserts sobre `dark.qss` (colores, grosor, sin flechas, sin colores claros).
- **E2E**: no aplica (QSS estático; la app ya carga el QSS y hay test de carga).
- **Nombre de archivos de test**: `tests/test_scrollbars.py`

## Notas de diseño
- Paleta existente: `#00ffaa` (fósforo), `#00aa70` (dim), track `#060b0b`. No se añaden colores nuevos.
- Precedente: `test_crono_mode_checked_verde_en_qss` y `test_matriz_qss_handle_visual` ya asertan QSS por texto.
