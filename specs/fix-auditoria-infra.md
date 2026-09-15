# SPEC: Auditoría de infraestructura y drift de spec (lote 2)

## Meta
- **Feature**: `fix-auditoria-infra`
- **Autor**: opencode
- **Fecha**: 2026-09-15
- **Estado**: `APPROVED`

## Objetivo
Cerrar los hallazgos de infraestructura y de drift de spec de la auditoría posterior al lote 1 (C4-C7):
1. C4: no existe script de build ni spec de PyInstaller reproducibles.
2. C5: `.mcp.json` apunta a una ruta inexistente (`D:\APP SQL OFFLINE` en vez de `D:\SALVA APP SQL OFFLINE`).
3. C6: no existe `.gitignore` (el repo no tiene ningún commit).
4. C7: `test_json_dialog_copy_button` puede pasar sin ejecutar ninguna aserción (test vacuo).
5. Drift SC-10: la spec de `sqlite-engine.md` exige que tras `close()` `table_names() = []`, pero la implementación deja `self.tables` intacta.

## Acceptance Criteria

### IA-01: close() cumple SC-10
- **Given** un motor conectado con tablas cargadas (`table_names()` no vacío)
- **When** se llama `close()`
- **Then** `connected` es `False` y `table_names()` es `[]`

### IA-02: test de copiar plantilla nunca pasa en vacío
- **Given** la ventana abierta y el modal de formato JSON mostrado
- **When** se ejecuta `test_json_dialog_copy_button`
- **Then** el test falla si no existe ningún botón `COPIAR PLANTILLA` (la aserción es obligatoria, no condicional)

### IA-03: .mcp.json apunta a la raíz real del proyecto
- **Given** el archivo `.mcp.json` en la raíz del repo
- **When** se valida la ruta de `filesystem.args`
- **Then** la ruta es `D:\SALVA APP SQL OFFLINE` (la raíz real del workspace)

### IA-04: existe .gitignore con las reglas mínimas del proyecto
- **Given** la raíz del repo
- **When** se comprueba la presencia del archivo
- **Then** existe `.gitignore` y excluye como mínimo: `__pycache__/`, `*.pyc`, `.pytest_cache/`, `dist/`, `build/`, `.venv/`, `*.spec` generado (no el `run.spec` fuente del repo), archivos `.db*` y archivos de sesión guardados (`sesion*.json`)

### IA-05: build reproducible con run.spec + script
- **Given** el repo limpio y PyInstaller instalado
- **When** se ejecuta `bin\build.ps1`
- **Then** genera `dist/SQLab.exe` con `--name SQLab`, `--onefile`, `--windowed`, sobre `app-sql-offline/app.py`, a partir de `run.spec` versionado
- **Then** el README y AGENTS.md documentan esa misma vía de build (sin duplicar comandos divergentes)

## Edge Cases
- [x] `close()` llamada dos veces seguidas no debe lanzar excepción
- [x] `close()` sin conexión previa (motor recién creado) → sigue `connected = False`, `table_names() = []`
- [ ] `run.spec` debe incluir los recursos (`.qss`, `.svg`) como datos para que el `.exe` conserve tema y logo
- [ ] Si PyInstaller no está instalado, `bin\build.ps1` debe mostrar mensaje de error claro y salir con código != 0

## Límites Conocidos
- El `.exe` se genera solo en Windows (plataforma objetivo del proyecto); el script es `build.ps1`.
- No se verifica automáticamente el binario generado en la suite de tests (requeriría PyInstaller en CI); la spec valida el script y la spec fuente.
- `.mcp.json` es específico del desarrollador (MCP servers para el editor); se corrige el path pero no se agrega a `.gitignore` por ser configuración de repo útil de compartir.

## Archivos a tocar
- `.mcp.json` (corregir ruta → C5)
- `.gitignore` (crear → C6)
- `bin/build.ps1` (crear → C4)
- `run.spec` (crear → C4)
- `app-sql-offline/core/sqlite_engine.py` (fix `close()` → SC-10)
- `app-sql-offline/tests/test_sqlite_engine.py` (assert `table_names() == []` tras close → RED)
- `app-sql-offline/tests/test_e2e_smoke.py` (fix tautología botón copia)
- `README.md` (alinear build con `run.spec`)
- `AGENTS.md` (changelog v12)

## Tests requeridos
- **Unit** (`tests/test_sqlite_engine.py`): `test_close_disconnects` ampliado a `e.table_names() == []` (RED antes del fix).
- **Unit** (`tests/test_sqlite_engine.py`): nuevo `test_close_double` (doblemente `close()` no debe lanzar).
- **Unit** (`tests/test_sqlite_engine.py`): nuevo `test_close_sin_conexion` (motor recién creado → `table_names() == []`).
- **E2E** (`tests/test_e2e_smoke.py`): `test_json_dialog_copy_button` pasa de `if copy_btns:` a `assert copy_btns` obligatorio.
- La suite completa debe seguir en verde: `python -m pytest -q` desde `app-sql-offline/`.

## Notas de diseño
- `close()` pasa a resetear `self.tables = {}` además de cerrar la conexión, cumpliendo SC-10 tal como está escrito en `specs/sqlite-engine.md` (la spec es la fuente de verdad; el módulo ya no es "NO TOCAR" para cumplir la propia spec).
- `run.spec` de PyInstaller se versiona en la raíz del repo; `bin/build.ps1` lo invoca (`pyinstaller run.spec`). Recurso crítico: `dark.qss` y `logo_sqllab.svg` como `datas` para que el exe conserve tema oscuro y logo.
- El fix de la tautología convierte una aserción opcional en obligatoria: si no existe el botón, el test debe fallar (no silenciosamente pasar).