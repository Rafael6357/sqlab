# SPEC: exportar-excel

## Meta
- **Feature**: exportar-excel
- **Autor**: opencode (Muse Spark)
- **Fecha**: 2026-09-18
- **Estado**: `APPROVED`

## Objetivo
Botón `EXPORTAR EXCEL` junto a `EXPORTAR CSV`: guarda el resultado completo
en `.xlsx` real (celdas, columnas y filas separadas que Excel abre directo),
porque el CSV con `,` se abre en una sola columna en locales con `;`.

## Acceptance Criteria

### XL-01 — botón y diálogo
- **Given** resultado visible
- **When** clic `EXPORTAR EXCEL`
- **Then** `getSaveFileName` (`Excel (*.xlsx)`, sugerido `resultado.xlsx`).

### XL-02 — contenido con celdas
- **Given** resultado con cabecera + filas (incl. `None`)
- **When** exportar
- **Then** el `.xlsx` trae cabecera en fila 1 y valores por celda; `None` → texto `NULL` (coherente con CSV v21); anchos de columna auto (tope 50).

### XL-03 — CSV intacto
- **Given** el botón `EXPORTAR CSV`
- **When** se usa
- **Then** comportamiento EX-01..EX-06 sin cambios.

### XL-04 — cancelar y vacío
- **Given** cancelar el diálogo / sin resultados
- **When** vuelve
- **Then** sin fichero (cancelar) o toast `SIN RESULTADOS // NADA QUE EXPORTAR` (vacío), sin crash.

## Edge Cases
- [x] Resultado de 1 fila / 1 columna.
- [x] Valores con saltos de línea: openpyxl los guarda en la celda.
- [x] Sobrescribir: lo decide el diálogo nativo.

## Límites Conocidos
- Exporta el último resultado (no el visor), igual que CSV.
- Sin formato (negritas/colores): solo datos + anchos.

## Archivos a tocar
- `ui/main_window.py` (`exportar_resultado_excel` + botón en cabecera)
- `tests/test_exportar_excel.py` (nuevo: XL-01..XL-04)

## Tests requeridos
- **Unit/E2E**: botón existe; roundtrip openpyxl (cabecera + filas + NULL); cancelar; vacío.
- **Nombre de archivos de test**: `tests/test_exportar_excel.py`

## Notas de diseño
- `openpyxl` ya es dependencia del proyecto (carga de `.xlsx`); sin deps nuevas.
