# SPEC: Carga de sesiones (JSON interno, formato IA y CSV)

- **Feature**: Carga y parseo de archivos de ejercicio para sesiones SQL de práctica
- **Estado**: IMPLEMENTADO (v1-v2)
- **Archivo**: `core/session_loader.py` (~253 líneas)
- **Tests**: `tests/test_session_loader.py` (18 tests)

## Objetivo
Parsear archivos de ejercicio (JSON formato interno, JSON formato IA, y CSV) y convertirlos en objetos `Table` + `Ejercicio` listos para inyectar en el `SQLEngine` en memoria.

## Acceptance Criteria

### Formato JSON Interno

#### SC-01: Carga de ejemplo tienda
- **Given** el archivo `examples/ejemplo_tienda.json` (formato interno, 2 tablas: clientes + pedidos)
- **When** se llama `load_file(path)`
- **Then** `LoadResult.ok = True`, `tables` tiene 2 tablas (`"clientes"`, `"pedidos"`), `ejercicio.titulo` contiene `"Gasto"`

#### SC-02: Carga de ejemplo biblioteca
- **Given** el archivo `examples/ejemplo_biblioteca.json` (3 tablas: libros + usuarios + prestamos)
- **When** se llama `load_file(path)`
- **Then** `tables` tiene 3 tablas con nombres correctos

#### SC-03: Tipos preservados correctamente
- **Given** un JSON con columna `"tipo": "INTEGER PRIMARY KEY"`
- **When** se parsea la tabla
- **Then** la columna conserva el tipo completo `"INTEGER PRIMARY KEY"` (no se trunca)

#### SC-04: Tipos inválidos se reemplazan por TEXT
- **Given** un JSON con columna `"tipo": "VARCHAR(255)"` (no está en `_VALID_TYPES`)
- **When** se parsea la tabla
- **Then** la columna tiene `"tipo": "TEXT"`

### Formato IA (alternativo)

#### SC-05: Normalización de formato IA completo
- **Given** un JSON con formato IA: `{"title": "Ej", "difficulty": "Intermedio", "statement": "Haz un JOIN", "expected_hint": "Pista", "tables": [{"name": "usuarios", "schema": {"id": "INTEGER PRIMARY KEY", "nombre": "TEXT"}, "data": [[1, "Ana"]]}]}`
- **When** se llama `load_file(path)`
- **Then** `_normalize_ia_format()` convierte a formato interno, `ejercicio.titulo = "Ej"`, `tables[0].name = "usuarios"`, `tables[0].columns[0].type = "INTEGER PRIMARY KEY"`

#### SC-06: Formato IA con defaultQuery
- **Given** un JSON IA con `"defaultQuery": "SELECT 1;"`
- **When** se normaliza
- **Then** `ejercicio.default_query = "SELECT 1;"`

### CSV

#### SC-07: Carga de CSV individual
- **Given** el archivo `examples/csv/clientes.csv` (4 columnas, 4 filas)
- **When** se llama `load_file(path)`
- **Then** `tables` tiene 1 tabla `"clientes"` con 4 columnas y 4 filas

#### SC-08: Inferencia de tipos CSV
- **Given** un CSV con columna de valores puramente enteros
- **When** se inferiere el tipo
- **Then** `column.type = "INTEGER"` (no TEXT)

#### SC-09: CSV vacío produce error
- **Given** un CSV con solo cabecera (0 filas de datos)
- **When** se parsea
- **Then** `LoadResult.ok = False`, error contiene `"vacío o solo tiene cabecera"`

#### SC-10: Carga de carpeta CSV
- **Given** una carpeta con 2 archivos CSV: `clientes.csv` y `productos.csv`
- **When** se llama `load_csv_folder(folder)`
- **Then** `tables` tiene 2 tablas con nombres de archivo

#### SC-11: Carpeta CSV vacía produce error
- **Given** una carpeta sin archivos .csv
- **When** se llama `load_csv_folder()`
- **Then** `LoadResult.ok = False`, error contiene `"csv"`

### Errores

#### SC-12: JSON inválido produce error descriptivo
- **Given** un archivo con contenido `{not valid json`
- **When** se llama `load_file()`
- **Then** `LoadResult.ok = False`, error contiene `"JSON válido"`

#### SC-13: JSON sin tablas produce error
- **Given** un JSON válido pero sin clave `"tablas"` ni `"tables"`
- **When** se llama `load_file()`
- **Then** `LoadResult.ok = False`, error contiene `"ninguna tabla"`

#### SC-14: Extensión no soportada produce error
- **Given** un archivo `.xml` o `.txt`
- **When** se llama `load_file()`
- **Then** `LoadResult.ok = False`, error contiene `"Formato no soportado"`

### Ejercicio defaults

#### SC-15: Ejercicio sin campos tiene defaults vacíos
- **Given** un `Ejercicio()` nuevo
- **When** se inspeccionan sus campos
- **Then** `titulo = ""`, `enunciado = ""`, `pista = ""`, `dificultad = "Principiante"`, `default_query = ""`

### Inferencia de tipos

#### SC-16: _infer_type con INTEGER
- **Given** el valor `"42"`
- **When** se llama `_infer_type("42")`
- **Then** retorna `"INTEGER"`

#### SC-17: _infer_type con REAL
- **Given** el valor `"3.14"`
- **When** se llama `_infer_type("3.14")`
- **Then** retorna `"REAL"`

#### SC-18: _infer_type con TEXT
- **Given** el valor `"hola"`
- **When** se llama `_infer_type("hola")`
- **Then** retorna `"TEXT"`

## Edge Cases
- Valores vacíos `""` en CSV: se convierten a `None` (NULL en SQLite)
- Valores `"null"`, `"NULL"`, `"None"`: se infieren como `TEXT`, se mantienen como string
- CSV con filas de largo desigual: se rellenan con `""` (vacíos → None)
- JSON con claves extra en tablas: se ignoran silenciosamente
- Tabla con nombre con espacios: se reemplazan por `_` en CSV

## Archivos a tocar
- `core/session_loader.py` (NO TOCAR — módulo base estable)

## Notas de diseño
- `_normalize_ia_format` es un adaptador que convierte formato IA → formato interno
- `_parse_json` detecta formato IA cuando `"tablas"` no existe pero sí `"tables"`
- `_infer_type` prueba int() → float() → fallback TEXT; valores vacíos siempre TEXT
- `LoadResult.ok` requiere al menos 1 tabla válida; errores se acumulan en `errors[]`
