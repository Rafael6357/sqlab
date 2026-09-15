# SPEC: Motor SQLite embebido

- **Feature**: Motor SQL en memoria para sesiones de práctica
- **Estado**: IMPLEMENTADO (v1+)
- **Archivo**: `core/sqlite_engine.py` (~108 líneas)
- **Tests**: `tests/test_sqlite_engine.py` (12 tests)

## Objetivo
Proveer un motor SQLite que mantenga tablas en memoria (`:memory:`), ejecute consultas SQL reales y devuelva resultados estructurados o errores traducidos al español.

## Acceptance Criteria

### SC-01: Inicialización sin conexión
- **Given** un `SQLEngine` recién creado
- **When** se consulta `connected`
- **Then** devuelve `False`

### SC-02: Carga de tablas conecta al motor
- **Given** un `SQLEngine` sin conexión y una lista de tablas `[Table("clientes", [Column("id","INTEGER"), Column("nombre","TEXT")], [[1,"Ana"]])]`
- **When** se llama `load_tables(tables)`
- **Then** `connected` devuelve `True`, `table_names()` incluye `"clientes"`

### SC-03: Ejecución de SELECT simple
- **Given** un motor conectado con tabla `clientes` (id INTEGER, nombre TEXT) con 1 fila
- **When** se ejecuta `SELECT * FROM clientes;`
- **Then** `QueryResult.ok = True`, `columns = ["id", "nombre"]`, `rows = [[1, "Ana"]]`, `row_count = 1`

### SC-04: Ejecución con WHERE
- **Given** tabla `clientes` con 4 filas (id: 1,2,3,4)
- **When** se ejecuta `SELECT nombre FROM clientes WHERE id = 1`
- **Then** `rows = [["Ana Pérez"]]`, `row_count = 1`

### SC-05: Error de sintaxis se traduce
- **Given** un motor conectado con tablas cargadas
- **When** se ejecuta `SELEC * FROM clientes;` (error de tipeo)
- **Then** `QueryResult.ok = False`, `error` contiene texto en español (via `error_friendly`)

### SC-06: Consulta vacía devuelve mensaje informativo
- **Given** un motor conectado
- **When** se ejecuta una cadena vacía o solo espacios/punto y coma
- **Then** `QueryResult.ok = True`, `message = "Escribe una consulta y pulsa Ejecutar."`

### SC-07: Sin tablas cargadas retorna error descriptivo
- **Given** un motor sin tablas (sin llamar a `load_tables` o con lista vacía)
- **When** se ejecuta cualquier consulta
- **Then** `QueryResult.ok = False`, `error` contiene "tablas cargadas"

### SC-08: Carga reemplaza sesión anterior
- **Given** motor conectado con tabla `A`
- **When** se llama `load_tables` con tabla `B`
- **Then** `table_names() = ["B"]` (tabla `A` ya no existe)

### SC-09: INSERT funciona y se refleja en SELECT
- **Given** motor con tabla `test` (id INTEGER, val TEXT)
- **When** se ejecuta `INSERT INTO test VALUES (1, 'ok')` seguido de `SELECT * FROM test`
- **Then** el SELECT retorna `[[1, "ok"]]`

### SC-10: close() cierra la conexión
- **Given** un motor conectado
- **When** se llama `close()`
- **Then** `connected = False`, `table_names() = []`

## Edge Cases
- Tabla vacía (0 filas): CREATE TABLE + SELECT retorna columnas pero `row_count = 0`
- CREATE TABLE执行后 no se refleja en `table_names()` (solo tablas de `load_tables`)
- Consulta sin punto y coma: funciona correctamente (se limpia strip(";"))
- Múltiples tablas con FK: SQLite permite sin habilitar `PRAGMA foreign_keys`

## Límites Conocidos
- ~50k filas por tabla (degradación de QTableWidget más allá)
- Tablas persistence solo durante la sesión (`:memory:`)
- Sin soporte de transacciones anidadas

## Archivos a tocar
- `core/sqlite_engine.py` (NO TOCAR — módulo base estable)

## Notas de diseño
- `row_factory = sqlite3.Row` para acceso por nombre de columna en dumps
- `QueryResult` es un dataclass con defaults para mensajes de éxito/error
- `friendly_error()` se invoca en el except final para traducir errores SQLite
