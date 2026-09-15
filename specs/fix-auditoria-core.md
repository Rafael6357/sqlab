# SPEC: Fix críticos — crash en core (error_friendly, session_loader, sqlite_engine)

> Feature ID: `fix-auditoria-core`

## Meta
- **Feature**: Corrección de 3 bugs CRÍTICOS que crashean la app sin recuperación (C1, C2, C3 del audit completo)
- **Autor**: audit (ai)
- **Fecha**: 2026-09-15
- **Estado**: `EN_PROGRESO`

## Objetivo
Eliminar los 3 crash paths detectados en la auditoría completa de la app. Ningún input malformado (mensaje SQLite raro, JSON de ejercicio malformado, datos de tabla inconsistentes) debe poder crashear el proceso; todos deben devolver errores/omisiones controladas.

1. **C1** — `core/error_friendly.py`: el patrón `table .* has (?:no column named|no such column)` usa la plantilla `«{1}»` pero solo tiene UN grupo de captura → `IndexError` escapa de `execute()`.
2. **C2** — `core/session_loader.py` `_parse_json()`: asume que cada entrada de `tablas`, `columnas` y `filas` tiene la forma esperada → `AttributeError` / `KeyError` con JSON malformado (p. ej. `tablas: [42]`).
3. **C3** — `core/sqlite_engine.py` `load_tables()`: sin ningún `try/except` sobre CREATE/INSERT → `OperationalError`/`InterfaceError` con filas de largo distinto, columnas duplicadas, cero columnas o celdas no escalares.

## Acceptance Criteria

### C1 — friendly_error nunca lanza IndexError

#### C1-01 — «table X has no column named Y» se traduce, no crashea
- **Given** el error crudo de SQLite `table clientes has no column named telefono`
- **When** se llama `friendly_error(raw)`
- **Then** retorna un string (sin excepción) que contiene `telefono` (o `teléfono`) y `columna`

#### C1-02 — «table X has no such column Y» se traduce, no crashea
- **Given** el error crudo `table pedidos has no such column total`
- **When** se llama `friendly_error(raw)`
- **Then** retorna un string (sin excepción) que referencia la columna

#### C1-03 — regresión: el resto de patrones sigue intacto
- **Given** los casos ya cubiertos (no such table, syntax error, datatype mismatch, etc.)
- **When** se ejecuta la suite existente `test_error_friendly.py`
- **Then** los 12+ tests pasan sin cambios de mensajes

### C2 — _parse_json tolera JSON malformado

#### C2-01 — entrada de tablas que no es un dict
- **Given** un JSON con `"tablas": [42]`
- **When** se llama `load_file(path)`
- **Then** `LoadResult.ok == False`, no lanza excepción, acumula un error descriptivo

#### C2-02 — columna que no es un dict
- **Given** un JSON con `"columnas": ["id"]` dentro de una tabla válida
- **When** se llama `load_file(path)`
- **Then** no lanza excepción; o bien devuelve `ok=False` con error, o bien omite esa columna con error acumulado

#### C2-03 — columna sin clave «nombre»
- **Given** un JSON con `"columnas": [{"tipo": "INTEGER"}]`
- **When** se llama `load_file(path)`
- **Then** no lanza `KeyError`; devuelve `ok=False` con error descriptivo o salta la columna acumulando error

#### C2-04 — filas que no son una lista de listas
- **Given** un JSON con `"filas": "todo"` (string) o `"filas": [[1], "x"]`
- **When** se llama `load_file(path)`
- **Then** no lanza excepción; las filas malformadas se saltan con error acumulado

#### C2-05 — tablas que no es una lista (dict o string)
- **Given** un JSON con `"tablas": {"clientes": {...}}` o `"tablas": 5`
- **When** se llama `load_file(path)`
- **Then** no lanza excepción; devuelve `ok=False` con error descriptivo

#### C2-06 — regresión: JSON válido sigue cargando
- **Given** `ejemplo_tienda.json`, `ejemplo_biblioteca.json` y el formato IA
- **When** se ejecuta la suite existente `test_session_loader.py`
- **Then** los 18+ tests pasan sin cambios de comportamiento

### C3 — load_tables tolera datos inconsistentes

#### C3-01 — fila con más valores que columnas
- **Given** tabla `t1` con 2 columnas y una fila `[1, 2, 3]`
- **When** se llama `load_tables([t1])`
- **Then** no lanza excepción; la fila se trunca a la cantidad de columnas y `t1` se carga

#### C3-02 — fila con menos valores que columnas
- **Given** tabla `t2` con 3 columnas y una fila `[1]`
- **When** se llama `load_tables([t2])`
- **Then** no lanza excepción; la fila se rellena con NULL y `t2` se carga

#### C3-03 — columnas duplicadas
- **Given** tabla `t3` con columnas `id`, `id`
- **When** se llama `load_tables([t3])`
- **Then** no lanza excepción; `t3` no queda en `table_names()` (CREATE falla, se omite)

#### C3-04 — tabla sin columnas
- **Given** tabla `t4` con `columns == []` y una fila
- **When** se llama `load_tables([t4])`
- **Then** no lanza excepción; `t4` no queda en `table_names()`

#### C3-05 — celda no escalar (lista/dict)
- **Given** tabla `t5` con una celda cuyo valor es `[1, 2]` (no escalar)
- **When** se llama `load_tables([t5])`
- **Then** no lanza `InterfaceError`; la fila/valor se normaliza (str) o la fila se omite

#### C3-06 — una tabla inválida no bloquea a las válidas
- **Given** `[tabla_invalida, tabla_valida]` donde la primera viola C3-03/C3-04
- **When** se llama `load_tables([...])`
- **Then** `tabla_valida` sí se carga y es consultable; no hay excepción

#### C3-07 — regresión: la suite existente pasa intacta
- **Given** `test_sqlite_engine.py` (12 tests) con `_sample_tables()` y los casos actuales
- **When** se ejecuta
- **Then** todos pasan sin cambios de comportamiento

## Edge Cases
- [x] Error SQLite con patrón C1 combinado con signos de puntuación en el nombre de columna
- [x] JSON con `tablas` no lista (`C2-05`)
- [x] Filas mixtas válidas + inválidas (`C2-04`)
- [x] `load_tables([])` sigue dejando el motor sin conexión (regresión SC-07/SC-02)
- [ ] `load_tables` con una tabla válida seguida de una inválida → ambas en el orden original
- [ ] C3 con `rows=None` (en vez de lista) → no explota (se trata como lista vacía/omitida)

## Límites Conocidos
- `load_tables` no valida nombres de tabla/columna; la omisión de una tabla inválida es silenciosa (no se notifica al UI todavía).
- La normalización de celdas no escalares la define la implementación concreta (str) y no cambia la semántica de la tabla para queries posteriores.
- `friendly_error` sigue usando el primer patrón que matchee; el orden de `_PATTERNS` no cambia.
- `close()` NO se modifica en esta spec (mantiene tablas en memoria por defecto; el drift con SC-10 queda como warning conocido del audit, no como bug que bloquea el lote 1).

## Archivos a tocar
- `app-sql-offline/core/error_friendly.py` — plantilla `{1}` → `{0}` en el patrón de tabla (línea 16)
- `app-sql-offline/core/session_loader.py` — guards de tipo en `_parse_json()` (aprox. líneas 152-181)
- `app-sql-offline/core/sqlite_engine.py` — robustez en `load_tables()` (aprox. líneas 58-76), sin dependencias de BD externas
- `app-sql-offline/tests/test_error_friendly.py` — tests C1-01, C1-02
- `app-sql-offline/tests/test_session_loader.py` — tests C2-01..C2-05
- `app-sql-offline/tests/test_sqlite_engine.py` — tests C3-01..C3-06

## Tests requeridos
- **Unit (test_error_friendly.py)**: C1-01, C1-02 (más regresión de la suite existente)
- **Unit (test_session_loader.py)**: C2-01..C2-05 con archivos temporales en `tmp_path`
- **Unit (test_sqlite_engine.py)**: C3-01..C3-06 sobre el motor real
- **Regresión**: las 3 suites completas + `test_e2e_smoke.py` deben seguir en verde

## Notas de diseño
- **C1**: solo cambiar el índice de la plantilla `{1}` → `{0}` (el patrón tiene un único grupo de captura). El `try/except IndexError` que ya existe en `friendly_error` sigue protegiendo el acceso a `m.group(1)`, pero el crash original estaba en `template.format(ident)`.
- **C2**: en `_parse_json`, validar con `isinstance` que `tablas_raw` sea `list`, cada `tbl` sea `dict`, `cols_raw` sea `list`, cada columna sea `dict` con clave `nombre`, y `rows_raw` sea iterable de listas. Acumular errores en `errors` y evitar crash. Si no queda ninguna tabla válida → `ok=False`.
- **C3**: envolver el bloque CREATE+INSERT por tabla y por fila; truncar/rellenar filas al largo de columnas; normalizar celdas no escalares con `str()`; omitir tablas cuyo CREATE falle (duplicadas/0 columnas) sin romper el resto. `self.tables` solo debe contener tablas creadas con éxito.
- Preservar `self.tables = {t.name: t for t in tables}` como fuente de verdad de nombres; no tocar `execute()` ni `close()` salvo lo imprescindible.