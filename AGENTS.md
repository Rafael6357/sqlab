# AGENTS.md

## Stack
- Python 3.11 + PySide6 6.10 + sqlite3 (stdlib, :memory:)
- Build: PyInstaller --onefile --windowed
- Tests: pytest + pytest-qt (ver `requirements-dev.txt`)

## Convenciones
- UI en español, solo modo oscuro (resources/dark.qss). No agregar modo claro.
- Tipos SQLite en mayúsculas: INTEGER, REAL, TEXT, NUMERIC, DATE, BOOLEAN.
- Editor SQL con SQLHighlighter (ui/sql_highlighter.py). No agregar dependencias de resaltado externas.
- Autocompletado apagado por defecto (QSettings autocompletado=false). Checkbox en main_window.
- Pista colapsada por defecto (QToolButton checkable, checked=False).
- Mensajes de error siempre vía core/error_friendly.py (español principiante).
- Lint: `ruff check .` (cuando esté configurado). Sin ESLint/Prettier.
- Tests: ejecutar desde `app-sql-offline/`: `python -m pytest -q` (offscreen automático).
- Decimales con punto en la BD; la UI los muestra tal cual.

## Metodología: Spec Driven Development
Todo el proyecto debe implementarse con **Spec Driven Development** para cada funcionalidad nueva:
1. **Spec** → escribir la especificación ANTES de tocar código, en `specs/<feature>.md` (objetivo, acceptance criteria Given/When/Then, edge cases, límites conocidos).
2. **Tests** → crear tests que validen la spec ANTES de implementar (TDD).
3. **Implement** → código que pase los tests.
4. **Verificar** → `python -m pytest -q` (desde `app-sql-offline/`) debe pasar al 100 %.
- No implementar funcionalidades sin spec previa en `specs/`.
- La spec debe incluir: objetivo, casos de uso, límites conocidos y requisitos de testing.
- Decisiones / trade-offs de diseño global → documentar en `design.md`.
- Tests existentes ya vinculados a specs vía `@pytest.mark.spec` (ver `conftest.py`, `SPEC_IDS`).
- Para features nuevas: copiar `specs/TEMPLATE.md`, llenarla y referenciarla en el changelog.

## Qué NO tocar
- Archivos .db generados (no hay persistencia salvo guardar sesión explícito).
- resources/dark.qss: no introducir variantes claras.
- core/sqlite_engine.py: no agregar dependencias de BD externas.

## Fuente de verdad
- `core/sqlite_engine.py` (~90 líneas): engine en memoria, execute().
- `core/session_loader.py` (~260 líneas): valida JSON/CSV + formato IA (`_normalize_ia_format`, `default_query`). Usar grep por `load_file` / `load_csv_folder`.
- `ui/main_window.py` (~1120 líneas): ventana principal SQLab (HUD/logo/mission/matrix/consola, dialogs custom `_show_custom_dialog`). Buscar por nombre de widget antes de leer completo.
- `tests/` (68 tests): `test_error_friendly.py` (12 unit), `test_sqlite_engine.py` (12 unit), `test_session_loader.py` (18 unit), `test_e2e_smoke.py` (26 E2E Qt offscreen).

## Changelog de contexto
- 2026-09: v12 — bugfix infraestructura (spec `fix-auditoria-infra`): `close()` cumple SC-10 (`table_names()` vacío tras cerrar, Double-safe); `.mcp.json` apunta a `D:\SALVA APP SQL OFFLINE`; creado `.gitignore`; build reproducible `bin\build.ps1` + `run.spec` (`--name SQLab`, onefile, windowed, datas de `resources/`); test de `COPIAR PLANTILLA` deja de ser tautológico (assert obligatorio); README alineado. Suite: 91 tests.
- 2026-09: v1 — carga JSON/CSV, pista colapsada, autocompletado OFF por defecto, historial, guardar/cargar sesión.
- 2026-09: v2 — rediseño estudio SQLStudio (descartado: diseño erróneo).
- 2026-09: v3 — Arcade Dojo (descartado: diseño erróneo).
- 2026-09: v4 — Postgres Studio Pro (descartado: diseño erróneo).
- 2026-09: v5 — CYBER-TERM TUI (base del diseño hacker).
- 2026-09: v6 — CYBER-TERM vigente, app 100 % en español (sin reloj/ticks, sin T1/T2/IO, sin NEXUS/AIR-GAPPED/LEVEL en inglés, sin tarjeta IA Link; niveles en español).
- 2026-09: v7 — app renombrada a SQL LEARN; HUD minimalista (sin versión/motor/heap/100% local); esquina de grilla oscura (QTableCornerButton); tooltips en toda la app; fuera ASCII-art y reglas QSS obsoletas.
- 2026-09: v8 — app renombrada a **SQLab**; logo `resources/logo_sqllab.svg` (ícono de ventana + chip HUD 26px); diálogos custom `_show_custom_dialog` en vez de `QMessageBox`; modal JSON con `COPIAR PLANTILLA` + toast in-dialog; `COPIAR PARA IA` con borde verde (`CyberBtn`); botón `FORMATO` como toggle (`FormatBtn:checked`); cabecera QSS e imports arreglados.
- 2026-09: v9 — bugfix `mostrar_formato_json` (`Claude`/`IA_PROMPT` → `CLAUDE_PROMPT`); suite de tests: 68 tests (unit + E2E) con pytest + pytest-qt offscreen; `requirements-dev.txt` + `pyproject.toml`.
- 2026-09: v10 — bugfix críticos (spec `fix-formatear-restablecer`): `formatear_consulta` ya no altera literales ni comentarios (state machine `_formatear_sql`); `restablecer_datos` recarga el preset original de arranque. Suite: 76 tests.
- 2026-09: v11 — bugfix crash en core (spec `fix-auditoria-core`): `friendly_error` ya no lanza IndexError en `table ... has no column named` (`{1}`→`{0}`); `_parse_json` tolera tablas/columnas/filas malformadas sin crashear; `load_tables` omite tablas inválidas (columnas duplicadas/sin columnas), trunca/rellena filas y normaliza celdas no escalares. Suite: 89 tests.
