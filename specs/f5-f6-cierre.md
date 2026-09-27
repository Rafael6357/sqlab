# SPEC: f5-f6-cierre (F5 suite final + F6 packaging)

## Meta
- **Feature**: f5-f6-cierre
- **Autor**: opencode (Muse Spark)
- **Fecha**: 2026-09-27
- **Estado**: `APPROVED`

## Objetivo
Cerrar la migración: suite 100 % en PG local, suite 100 % en modo CI (sin
binarios → skip PG + fallback SQLite), CI con `ruff`, docs finales y
checklist de máquina limpia.

## Acceptance Criteria

### CI-01 — verde en PG
- **Given** máquina con binarios
- **When** `python -m pytest -q` + `ruff check .`
- **Then** 100 % passed, 0 ruff, PG-tests ejecutados (no skipped).

### CI-02 — verde sin binarios (simulacro CI)
- **Given** `D:\pg-bin` oculto (simula CI)
- **When** `python -m pytest -q`
- **Then** 100 % passed, tests PG en `skipped`, UI en SQLite, sin errores de colección (psycopg instalado igual).

### CI-03 — workflow
- **Given** `.github/workflows/tests.yml`
- **When** se revisa
- **Then** instala requirements (incl. `psycopg`, `PySide6-Addons`) y corre `ruff check .` + `pytest -q` en 3.11 y 3.14.

### CI-04 — docs y checklist
- **Given** repo final
- **When** se lee README/AGENTS/design
- **Then** documentan motor PG, build con `pgsql/` (origen `D:\pg-bin\vendor`), exe ~145 MB, arranque async y checklist de máquina limpia.

## Edge Cases
- [x] `import ui.main_window` sin `psycopg` instalado: funciona (import lazy en `PGEngine`).
- [x] `import core.pg_engine` sin `psycopg`: funciona (lazy); `PGEngine()` falla con mensaje claro.

## Límites Conocidos
- La prueba en máquina limpia real la hace el usuario (checklist); aquí se verifica bundle + smoke.
- Sin binarios no hay e2e PG: los skip son el comportamiento diseñado, no deuda.

## Archivos a tocar
- `.github/workflows/tests.yml` (paso ruff)
- `README.md`, `AGENTS.md`, `design.md` (cierre)
- `tests/` solo si el simulacro revela fugas del fallback

## Tests requeridos
- **E2E**: las dos corridas completas (PG y simulacro).
- Sin archivo nuevo (verificación + docs).
