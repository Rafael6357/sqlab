# specs/INDEX.md — Mapa de specs ↔ tests ↔ design.md

> **Última actualización**: 2026-09-15 — RETROACTIVO para features v1-v9 existentes.
> Specs retroactivas creadas sin tests escritos antes de la implementación (ver AGENTS.md Metodología).

| Spec ID | Archivo spec | Archivos a testear | Tests existentes | design.md |
|---|---|---|---|---|
| `sqlite-engine` | `specs/sqlite-engine.md` | `core/sqlite_engine.py` | `tests/test_sqlite_engine.py` (12) | Líneas 3-10 |
| `error-friendly` | `specs/error-friendly.md` | `core/error_friendly.py` | `tests/test_error_friendly.py` (12) | Líneas 13 |
| `session-loader` | `specs/session-loader.md` | `core/session_loader.py` | `tests/test_session_loader.py` (18) | Líneas 59-64 (formato JSON dual) |
| `ui-main-window` | `specs/ui-main-window.md` | `ui/main_window.py` | `tests/test_e2e_smoke.py` (26) | Líneas 26-57 (UI SQLab) |
| `sql-highlighter` | `specs/sql-highlighter.md` | `ui/sql_highlighter.py` | *(sin tests unitarios dedicados)* | Convenciones AGENTS.md |
| `cronometro-ejercicio` | `specs/cronometro-ejercicio.md` | `ui/main_window.py` (+ `dark.qss`) | `tests/test_cronometro.py` (18) | design.md (UI SQLab — crono HUD) |
| `icono-ejecutable` | `specs/icono-ejecutable.md` | `bin/make_icon.py`, `run.spec` | `tests/test_icono.py` (3) | — |

## Notas sobre status retroactivo
- Todas las features listadas arriba ya están **implementadas** (v1-v9).
- Tests fueron escritos **después** de la implementación (retroactive characterization tests).
- Las specs se crearon **ahora** para documentar el comportamiento existente.
- Para **nuevas features**, seguir el ciclo completo Spec → Test → Implementar → Verificar.
