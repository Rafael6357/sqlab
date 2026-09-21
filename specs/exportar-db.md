# SPEC: exportar-db

## Meta
- **Feature**: exportar-db
- **Autor**: opencode (Muse Spark)
- **Fecha**: 2026-09-21
- **Estado**: `APPROVED`

## Objetivo
Botón `EXPORTAR DB` que vuelca la BD en memoria a un fichero `.db` real
(API `backup` de sqlite3): cierra el círculo con abrir `.db` (Fase A1) y
permite seguir el análisis fuera de SQLab.

## Acceptance Criteria

### ED-01 — roundtrip
- **Given** tablas cargadas en memoria
- **When** exportar y reabrir con `load_file`
- **Then** mismas tablas, columnas, filas y nulos.

### ED-02 — botón y diálogo
- **Given** sesión con datos
- **When** clic `EXPORTAR DB` (HUD, junto a GUARDAR SESIÓN)
- **Then** `getSaveFileName` (`SQLite (*.db)`, sugerido `base.db`); toast `BASE EXPORTADA: ... (N TABLAS)`.

### ED-03 — sin datos / cancelar
- **Given** sin tablas / diálogo cancelado
- **When** clic
- **Then** toast `SIN DATOS // NADA QUE EXPORTAR` (sin diálogo si no hay datos); cancelar no crea fichero ni toast de éxito.

## Edge Cases
- [x] Sobrescribir existente: lo decide el diálogo nativo.
- [x] Tablas con nombres raros/unicode: el `backup` copia páginas, sin re-CREATE.

## Límites Conocidos
- Vuelca el estado actual de la memoria (incluye DDL/DML de la sesión).
- Sin progreso para BDs gigantes (mismo límite práctico que la carga).

## Archivos a tocar
- `core/sqlite_engine.py` (`SQLEngine.exportar_db`)
- `ui/paneles.py` (botón) + `ui/main_window.py` (handler + señal)
- `tests/test_exportar_db.py` (nuevo: ED-01..ED-03)

## Tests requeridos
- **Unit/E2E**: roundtrip engine→fichero→loader; vacío/cancelar; botón existe.
- **Nombre de archivos de test**: `tests/test_exportar_db.py`

## Notas de diseño
- `sqlite3.Connection.backup()`: copia consistente sin SQL manual; stdlib, sin deps.
