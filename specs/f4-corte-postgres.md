# SPEC: f4-corte-postgres (F4)

## Meta
- **Feature**: f4-corte-postgres
- **Autor**: opencode (Muse Spark)
- **Fecha**: 2026-09-27
- **Estado**: `APPROVED`

## Objetivo
La app corre sobre PostgreSQL embebido: `MainWindow` acepta motor inyectado,
arranque async en producción (initdb 9 s la primera vez), conftest dual
(PG compartido o SQLite fallback sin binarios), y toda la UI con nombres SQLite (`DIALECTO: SQLITE3`, `DB: MEMORIA OK`, `EXCEPCIÓN_SINTAXIS_SQLITE`,
`0x22`) pasa a dialect-aware. `sqlite_engine.py` congelado salvo 2 attrs.

## Acceptance Criteria

### FC-01 — inyección y arranque
- **Given** `MainWindow(engine=eng)` / `MainWindow()`
- **When** arranca
- **Then** con engine: preset cargado directo, sin hilo; sin engine: hilo `_HiloArranque`, estado `INICIANDO MOTOR POSTGRESQL...`, preset al estar listo; sin binarios: diálogo fatal sin crash.

### FC-02 — guards
- **Given** motor aún `None`
- **When** EJECUTAR/CARGAR/GUARDAR/EXPORTAR
- **Then** toast `MOTOR INICIANDO...`, sin excepción.

### FC-03 — dialect-aware
- **Given** engine PG o SQLite
- **When** se mira la UI
- **Then** `DIALECTO: {dialect}`, status `DB: {etiqueta} OK`, título error `ERROR SQL` + código `CÓD: {dialect}`; `closeEvent` cierra el motor (None-safe).

### FC-04 — PG nativo en UI
- **Given** motor PG
- **When** `SELECT '5'::INTEGER`, `date_part`, `USING`, formateo con `RETURNING`/`ILIKE`
- **Then** ejecuta y formatea (keywords PG en el formateador); `Decimal` alinea a la derecha.

### FC-05 — conftest dual
- **Given** máquina con/sin binarios PG
- **When** `pytest -q`
- **Then** con binarios: servidor PG de sesión + BD fresca por test; sin binarios: `SQLEngine` (los tests PG-puros se saltan, el resto corre).

## Edge Cases
- [x] Servidor caído a mitad de sesión: `close()` tolerante (ya en F1).
- [x] `Decimal`/`date`/`bool` en grillas, CSV, Excel y comparador (hasheables/str OK).
- [x] `_build_ui` duplicado (Fase 3 lo dejó en ambos): se queda el del mixin.

## Límites Conocidos
- Primer arranque con initdb: ~9 s con aviso (una sola vez por máquina).
- `sqlite_engine.py` recibe solo `dialect`/`etiqueta_db` (congelado en lo demás).
- CI sin binarios: corre la suite en SQLite (los PG-puros hacen skip).

## Archivos a tocar
- `core/pg_engine.py` (`PGServer` + `PGEngine(server, dbname)`)
- `core/sqlite_engine.py` (solo `dialect`/`etiqueta_db`)
- `ui/main_window.py` (inyección, async, guards, `_refresh_dialecto`)
- `ui/workspace.py` (labels dinámicos), `ui/paneles.py` (status inicial neutro), `ui/carga.py` (status con etiqueta)
- `ui/formato_sql.py` (keywords PG + `RETURNING` cláusula), `ui/tablas.py` (`Decimal`)
- `tests/conftest.py` (dual), `tests/test_corte_pg.py` (nuevo: FC-01..FC-04)

## Tests requeridos
- **Unit/E2E**: inyección, guards, labels por engine, `::`/date_part en UI, formato PG, Decimal, closeEvent, conftest dual.
- **Nombre de archivos de test**: `tests/test_corte_pg.py`

## Notas de diseño
- `engine.dialect` (`SQLITE3`/`POSTGRESQL`) y `engine.etiqueta_db` (`MEMORIA`/`PG LOCAL`) evitan `if` por motor en la UI.
- MRO intacto; equivalencia por suite (que ahora corre en PG aquí y en SQLite en CI).
