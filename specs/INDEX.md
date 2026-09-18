# specs/INDEX.md — Mapa de specs ↔ tests ↔ design.md

> **Última actualización**: 2026-09-18 — v23 (normalizar-nulos-csv-excel).
> Specs retroactivas v1-v9 sin TDD; v10+ con ciclo Spec→Test→Implement completo.

| Spec ID | Archivo spec | Archivos a testear | Tests existentes | design.md |
|---|---|---|---|---|
| `sqlite-engine` | `specs/sqlite-engine.md` | `core/sqlite_engine.py` | `tests/test_sqlite_engine.py` (20) | Líneas 3-10 |
| `error-friendly` | `specs/error-friendly.md` | `core/error_friendly.py` | `tests/test_error_friendly.py` (14) | Líneas 13 |
| `session-loader` | `specs/session-loader.md` | `core/session_loader.py` | `tests/test_session_loader.py` (23) | Líneas 59-64 (formato JSON dual) |
| `ui-main-window` | `specs/ui-main-window.md` | `ui/main_window.py` | `tests/test_e2e_smoke.py` (34) | Líneas 26-57 (UI SQLab) |
| `sql-highlighter` | `specs/sql-highlighter.md` | `ui/sql_highlighter.py` | *(sin tests unitarios dedicados)* | Convenciones AGENTS.md |
| `cronometro-ejercicio` | `specs/cronometro-ejercicio.md` | `ui/main_window.py` (+ `dark.qss`) | `tests/test_cronometro.py` (20) | design.md (UI SQLab — crono HUD) |
| `icono-ejecutable` | `specs/icono-ejecutable.md` | `bin/make_icon.py`, `run.spec` | `tests/test_icono.py` (3) | — |
| `fix-matriz-resultados` | `specs/fix-matriz-resultados.md` | `ui/main_window.py`, `resources/dark.qss` | `tests/test_fix_matriz.py` (6) | design.md (splitter matriz/editor) |
| `carga-tablas-excel-csv` | `specs/carga-tablas-excel-csv.md` | `core/session_loader.py`, `ui/main_window.py`, `run.spec` | `tests/test_carga_tablas.py` (15) | design.md (carga tablas Excel/CSV) |
| `fix-ejemplos-empaquetados` | `specs/fix-ejemplos-empaquetados.md` | `ui/main_window.py` (`_bundle_dir`), `run.spec` (datas) | `tests/test_ejemplos_empaquetados.py` (7) | design.md (ejemplos en el bundle) |
| `carga-tablas-archivos` | `specs/carga-tablas-archivos.md` | `core/session_loader.py` (`combinar_resultados`), `ui/main_window.py` | `tests/test_carga_archivos.py` (11) | design.md (carga por archivos) |
| `formato-sql-real` | `specs/formato-sql-real.md` | `ui/main_window.py` (`_formatear_sql`, `_tokenizar_sql`) | `tests/test_formato_sql.py` (12) | design.md (formateador SQL) |
| `ui-nombres-estado` | `specs/ui-nombres-estado.md` | `ui/main_window.py`, `app.py` | `tests/test_ui_nombres.py` (36) | design.md (nombres + estado + maximizada) |
| `visor-tablas-anchas` | `specs/visor-tablas-anchas.md` | `ui/main_window.py` (`_configurar_grilla_ancha`, `_item_grilla`) | `tests/test_visor_tablas.py` (6) | design.md (grillas anchas) |
| `rendimiento-tablas-grandes` | `specs/rendimiento-tablas-grandes.md` | `ui/main_window.py` (topes, muestreo, aviso), `core/sqlite_engine.py` (`executemany`) | `tests/test_rendimiento.py` (7) | design.md (rendimiento) |
| `fix-carga-robusta` | `specs/fix-carga-robusta.md` | `core/session_loader.py` (BOM, headers), `core/sqlite_engine.py` (omitidas), `ui/main_window.py` | `tests/test_fix_carga_robusta.py` (5) | design.md (carga robusta) |
| `fix-multi-sentencia` | `specs/fix-multi-sentencia.md` | `core/sqlite_engine.py` (`_partir_sentencias`) | `tests/test_multi_sentencia.py` (7) | design.md (multi-sentencia) |
| `exportar-resultado-csv` | `specs/exportar-resultado-csv.md` | `ui/main_window.py` (`exportar_resultado_csv`) | `tests/test_exportar_csv.py` (6) | design.md (exportar CSV) |
| `mostrar-null-en-grillas` | `specs/mostrar-null-en-grillas.md` | `ui/tablas.py` (`_item_grilla`, `_ajustar_anchos`), `ui/main_window.py` (export) | `tests/test_mostrar_null.py` (6) | design.md (NULL visible) |
| `normalizar-nulos-csv-excel` | `specs/normalizar-nulos-csv-excel.md` | `core/session_loader.py` (`_es_nulo`, `_parse_csv`, `_parse_excel`) | `tests/test_normalizar_nulos.py` (7) | design.md (nulos CSV/Excel) |

## Notas sobre status retroactivo
- Todas las features listadas arriba ya están **implementadas** (v1-v9).
- Tests fueron escritos **después** de la implementación (retroactive characterization tests).
- Las specs se crearon **ahora** para documentar el comportamiento existente.
- Para **nuevas features**, seguir el ciclo completo Spec → Test → Implementar → Verificar.
