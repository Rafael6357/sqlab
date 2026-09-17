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
- `core/session_loader.py` (~490 líneas): valida JSON/CSV/XLSX/XLS + formato IA (`_normalize_ia_format`, `default_query`) + `combinar_resultados` (multi-archivo, last-wins). Usar grep por `load_file` / `load_tablas_folder` (alias `load_csv_folder`).
- `ui/main_window.py` (~1630 líneas): ventana principal SQLab (HUD/logo/mission/matrix/consola, `work_splitter` editor|matriz, `_formatear_sql`/`_tokenizar_sql`, `status_db`, dialogs custom `_show_custom_dialog`). Buscar por nombre de widget antes de leer completo.
- `tests/` (214 tests): `test_error_friendly.py` (14), `test_sqlite_engine.py` (20), `test_session_loader.py` (23), `test_e2e_smoke.py` (34), `test_cronometro.py` (20), `test_icono.py` (3), `test_fix_matriz.py` (6), `test_carga_tablas.py` (15), `test_ejemplos_empaquetados.py` (7), `test_carga_archivos.py` (11), `test_formato_sql.py` (12), `test_ui_nombres.py` (36), `test_visor_tablas.py` (6), `test_rendimiento.py` (7).

## Changelog de contexto
- 2026-09: v18 — feature SDD (spec `rendimiento-tablas-grandes`): topes de render (`VISOR_MAX_FILAS=2000`, `RESULTADO_MAX_FILAS=5000`, conteos y badge con total + aviso `MOSTRANDO N`), anchos por muestreo (`MUESTRA_MEDICION=100`, `Interactive` en vez de `ResizeToContents`), confirmación previa si archivos > `AVISO_MB=50` (`[CARGAR]`/`[CANCELAR]`, en archivos/carpeta/ejercicio/sesión), `executemany` con fallback fila por fila en `load_tables`. Suite: 214 tests.
- 2026-09: v17 — bugfix SDD (spec `visor-tablas-anchas`): tabla real ~200 cols × 221 filas se veía "vacía" (Stretch global → ~6 px/columna, padding QSS recortaba todo; parseo verificado intacto con SELECT de 4 cols); `_configurar_grilla_ancha` en visor y resultado (`ResizeToContents` + tope 300 px + `stretchLastSection` + elide derecha, `setWordWrap(False)`), `_item_grilla` con tooltip de valor completo; bugfix aislamiento `QSettings` en `conftest.py` (el ctor implícito usa registro nativo: snapshot + clear + restore por test, conserva preferencia real del usuario). Suite: 207 tests.
- 2026-09: v16 — features SDD (specs `carga-tablas-archivos` + `formato-sql-real` + `ui-nombres-estado`): botón `CARGAR TABLAS` con mini-diálogo custom `[ARCHIVOS]` (multi-selección `getOpenFileNames` `*.csv/*.xlsx/*.xls`) / `[CARPETA]` (intacto), `combinar_resultados` (last-wins + toast `REEMPLAZADA(S)`, errores por fichero sin bloquear válidos); `FORMATO SQL` real (`_tokenizar_sql` + cláusulas con salto/indent 2esp, subconsultas +1, `AND/OR/ON` indentados, `=` espaciado, literales/comentarios intactos, idempotente, ya no checkable); 14 renombres (`CONTENIDO DE LA TABLA`, `HISTORIAL DE CONSULTAS`, `ESQUEMA DE TABLAS`, `RESULTADO DE LA CONSULTA`, `[EJERCICIO]`, `GUARDAR/CARGAR SESIÓN`, `AUTOCOMPLETAR`, `PISTA:`, `TABLA ACTIVA:`, `N REGISTROS`, `EN MEMORIA`, `PLANTILLA JSON PARA IA`); barra `status_db` real (`TABLAS: N · FILAS: M · DB: MEMORIA OK`, fuera `CACHÉ_TX`/`PRAGMA` decorativos); `app.py` `showMaximized()`; bugfix race `QTimer.singleShot` en modal JSON (`_clear_toast` con try/except). Suite: 201 tests.
- 2026-09: v15 — bugfix SDD (spec `fix-ejemplos-empaquetados`): `EJEMPLO: TIENDA/BIBLIOTECA` fallaban en el exe (`...\_MEI...\examples\...` no existe porque `run.spec` solo empaquetaba `resources/`); `run.spec` añade `app-sql-offline/examples → examples` (incluye `examples/csv/`), `MainWindow._bundle_dir()` (`sys._MEIPASS` en frozen, `app-sql-offline/` en dev, fallback dev si falta `_MEIPASS`) y `cargar_preset` lo usa; funciona en otro dispositivo sin archivos externos (solo lectura en bundle). Suite: 142 tests.
- 2026-09: v14 — bugfix + feature SDD (specs `fix-matriz-resultados` + `carga-tablas-excel-csv` + `crono verdoso`): splitter editor|matriz nunca colapsa a 0 (`work_splitter` `setChildrenCollapsible(False)` + `setCollapsible(0/1,False)`, `editor_pane` 220 / `output_pane` 240, `handleWidth` 6 con QSS `margin:0 2px` + método `_reset_work_splitter` por doble-clic, `QSplitter::handle:horizontal` 1px visual); carga de tablas desde carpeta con `*.csv` (UTF-8/BOM, `,`/`;` auto) + `*.xlsx` (`openpyxl` read_only, `data_only`) + `*.xls` (`xlrd` 2.0.1) — solo 1ª hoja, `load_tablas_folder` (alias `load_csv_folder`) case-insensitive, `load_file` dispatch por ext., cabeceras vacías→`colN` y duplicadas→`_2`; botón `CSV` → `TABLAS` con tooltip formato completo; `run.spec` `hiddenimports=['openpyxl','xlrd']`; `requirements-dev.txt` añade `openpyxl`/`xlrd`/`xlwt`; `CronoMode:checked` pasa de ámbar a verde sólido (`#00ffaa`/`rgba(0,255,170,0.15)`, test `test_crono_mode_checked_verde_en_qss`). Suite: 135 tests.
- 2026-09: v13 — features SDD (specs `cronometro-ejercicio` + `icono-ejecutable`): cronómetro/temporizador por ejercicio en HUD (`CronoFrame`: `CRONO`/`TEMPO`, `INICIAR`/`PAUSA`, `REINICIAR`, spin 5–3600 s, reset automático al cargar ejercicio, toast `TIEMPO AGOTADO`); exe con icono del logo (`bin/make_icon.py` SVG→ICO multi-tamaño, `icon=` en `run.spec`). Suite: 91 + nuevos tests.
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
