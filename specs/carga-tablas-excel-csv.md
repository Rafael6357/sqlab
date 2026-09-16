# SPEC: carga-tablas-excel-csv — Carga robusta de tablas desde CSV y Excel

- **Feature**: Carga de tablas desde carpeta con `*.csv` / `*.xlsx` / `*.xls` (UTF-8)
- **Autor**: agente
- **Fecha**: 2026-09-16
- **Estado**: APPROVED

## Objetivo
Que la app acepte, además de `*.csv` UTF-8, ficheros Excel `*.xlsx` / `*.xls` desde la misma carpeta; que sea tolerante a casos reales (mayúsculas, BOM, `;`) y que el diálogo explique exactamente qué formato acepta.

## Acceptance Criteria

### EC-01: Formato CSV documentado y visible en UI
- **Given** el botón `TABLAS` (antes `CSV`) en el HUD
- **When** el usuario hace hover o abre el diálogo de carpeta
- **Then** tooltip + título del diálogo indican: *carpeta con `*.csv` UTF-8 (BOM opcional), cabecera en fila 1, delimitador `,` o `;` auto-detectado, 1 fichero = 1 tabla, nombre tabla = nombre fichero, ext. insensible a mayúsculas, ≥1 fila de datos*

### EC-02: CSV mayúsculas / BOM / ; cargan
- **Given** una carpeta con `DATOS.CSV` (mayúsculas), `datos_bom.csv` (UTF-8 con BOM `\ufeff`), `datos_semi.csv` (delimitado por `;`)
- **When** `load_file` / `load_tablas_folder` (alias `load_csv_folder`)
- **Then** `ok=True`, cada fichero produce 1 tabla con cabeceras normalizadas y filas correctas

### EC-03: Excel .xlsx primera hoja
- **Given** carpeta con `ventas.xlsx` (hoja1: fila1 cabeceras, resto datos)
- **When** se carga la carpeta
- **Then** `ok=True`, tabla `ventas` con columnas = cabeceras de hoja1, filas = datos de hoja1 (valores tal cual, `None` si celda vacía)

### EC-04: Excel .xls legacy primera hoja
- **Given** carpeta con `listado.xls` (BIFF, hoja1 con cabecera)
- **When** se carga
- **Then** `ok=True`, tabla `listado` equivalente a EC-03

### EC-05: Carpeta mixta csv + xlsx + xls
- **Given** carpeta con `a.csv`, `b.XLSX`, `c.Xls`
- **When** `load_tablas_folder`
- **Then** `tables` contiene 3 tablas; `table_names()` incluye las 3; errores vacíos

### EC-06: Errores explícitos y no crash
- **Given** carpeta vacía / fichero solo cabecera / libro sin hojas / cabecera vacía
- **When** carga
- **Then** `ok=False` o tabla con cabecera normalizada a `col{n}` sin crash; mensaje en español menciona fichero y motivo (`vacío o solo tiene cabecera`, `No se encontraron archivos *.csv/*.xlsx/*.xls`)

## Edge Cases
- [ ] Cabecera vacía/duplicada → `col{n}` / sufijo `_2`
- [ ] Filas desiguales en Excel → relleno `None`, truncado a `len(columns)`
- [ ] Celdas no escalares / fórmulas → `str` / valor calculado
- [ ] Carpeta sin ficheros válidos → `No se encontraron archivos *.csv/*.xlsx/*.xls en:`
- [ ] `*.CSV` / `*.XLSX` mayúsculas
- [ ] BOM + `;` combinados
- [ ] Libro multi-hoja: solo 1ª hoja (documentado en Límites)

## Límites Conocidos
- Solo 1ª hoja de cada libro; no fórmulas dinámicas (valor cacheado por Excel); no `.xlsb`/`.ods`/`.xlsm` macro; tamaño práctico < 50k filas / ~10MB por fichero; tipos Excel inferidos como CSV (INTEGER/REAL/TEXT, luego Create adaptado por `sqlite_engine`).
- Dependencia: `openpyxl` para `.xlsx`, `xlrd==2.0.1` para `.xls` legacy (añadidas a `requirements-dev.txt` y `run.spec`).

## Archivos a tocar
- `core/session_loader.py` (`_parse_csv` con `utf-8-sig` + sniffer `,;` + normalización cabeceras, nuevo `_parse_excel`, `load_file` dispatch, `load_csv_folder` → `load_tablas_folder` + alias)
- `ui/main_window.py` (botón `CSV` → `TABLAS`, `cargar_csv_carpeta` → `cargar_tablas_carpeta` + alias, tooltip/título diálogo)
- `requirements` / `run.spec` (hiddenimports `openpyxl`, `xlrd`)
- `specs/carga-tablas-excel-csv.md`, `design.md` si aplica

## Tests requeridos
- **Unit**: `tests/test_carga_tablas.py` (o ampliar `test_session_loader.py`)
  - `test_csv_uppercase_ext`, `test_csv_bom`, `test_csv_semicolon`, `test_csv_only_header_error`
  - `test_xlsx_first_sheet`, `test_xls_legacy`, `test_mixed_folder_csv_xlsx_xls`, `test_empty_folder_error_mentions_all_exts`
- **E2E**: `tests/test_e2e_smoke.py` o `tests/test_fix_excel` — cargar carpeta mixta vía `load_tablas_folder` + `_aplicar_resultado` y verificar `engine.table_names()`.

## Notas de diseño
- BOM: `open(..., encoding="utf-8-sig")` absorbe `\ufeff`; sniffer `csv.Sniffer` para `,;`.
- Case-insensitive: filtro `p.suffix.lower() in {".csv",".xlsx",".xls"}` en vez de `glob("*.csv")`.
- Excel: `openpyxl.load_workbook(..., data_only=True, read_only=True)` para `.xlsx`; `xlrd.open_workbook(..., on_demand=True)` para `.xls`; iterar `iter_rows(values_only=True)`.
