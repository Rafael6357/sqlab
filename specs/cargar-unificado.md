# SPEC: cargar-unificado

## Meta
- **Feature**: cargar-unificado
- **Autor**: opencode (Muse Spark)
- **Fecha**: 2026-09-18
- **Estado**: `APPROVED`

## Objetivo
Un solo botón **CARGAR** en el HUD reemplaza `CARGAR EJERCICIO (.json)` y
`CARGAR TABLAS`: al clic abre el diálogo de origen ampliado con
`[EJERCICIO] [ARCHIVOS] [CARPETA] [CANCELAR]`. Mismo objetivo (cargar una
base para trabajar), una sola entrada.

## Acceptance Criteria

### CU-01 — botón único
- **Given** el HUD
- **When** se mira
- **Then** existe `btn_cargar` con texto `CARGAR` y tooltip que documenta `.json` + `*.csv/*.xlsx/*.xls/*.db`; ya no existen botones separados de ejercicio/tablas.

### CU-02 — despacho por origen
- **Given** el diálogo de origen
- **When** `EJERCICIO` / `ARCHIVOS` / `CARPETA` / `CANCELAR`
- **Then** `_elegir_modo_carga()` devuelve `ejercicio` / `archivos` / `carpeta` / `None`, y `cargar_unificado()` despacha a `cargar_json()` / `cargar_tablas_archivos()` / `cargar_csv_carpeta()` / nada.

### CU-03 — compatibilidad
- **Given** la suite existente
- **When** corre
- **Then** los métodos `cargar_json`, `cargar_tablas_archivos`, `cargar_csv_carpeta` y `cargar_tablas` siguen existiendo (delegan al flujo unificado); `ARCHIVOS`/`CARPETA` conservan su texto.

## Edge Cases
- [x] Cancelar: sin cambios, sin diálogos extra.
- [x] Presets y PLANTILLA JSON PARA IA: intactos (fuera del alcance D1).
- [x] `.db` llega por ARCHIVOS/CARPETA (filtros ya lo incluyen, Fase A1).

## Límites Conocidos
- El diálogo sigue siendo custom (`_show` no aplica: usa `QDialog` directo como hoy).

## Archivos a tocar
- `ui/paneles.py` (`_build_hud`: botón único)
- `ui/main_window.py` (`_elegir_modo_carga`, `cargar_unificado`, `_connect_signals`)
- `tests/test_carga_archivos.py` (CU-02/CU-03), `tests/test_carga_tablas.py` + `tests/test_ui_nombres.py` (botón nuevo)

## Tests requeridos
- **Unit/E2E**: modo `ejercicio`; despacho a `cargar_json`; botón `CARGAR` existe y tooltip documenta formatos; viejos `btn_load`/`btn_csv` ausentes.
- **Nombre de archivos de test**: `tests/test_carga_archivos.py` (extender)

## Notas de diseño
- No se tocan loaders ni engine: solo UI + despacho.
