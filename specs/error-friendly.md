# SPEC: Errores amigables en español

- **Feature**: Traducción de errores SQLite a español para principiantes
- **Estado**: IMPLEMENTADO (v1+)
- **Archivo**: `core/error_friendly.py` (~43 líneas)
- **Tests**: `tests/test_error_friendly.py` (12 tests)

## Objetivo
Traducir automáticamente los mensajes de error crípticos de SQLite a mensajes claros en español, orientados a usuarios principiantes que están aprendiendo SQL.

## Acceptance Criteria

### SC-01: Tabla inexistente
- **Given** una consulta que referencia una tabla que no existe
- **When** se genera el error de SQLite `no such table: X`
- **Then** `friendly_error()` retorna un mensaje conteniendo `«X»` y `"Revisa la lista de tablas"`

### SC-02: Columna inexistente
- **Given** una consulta que referencia una columna que no existe
- **When** se genera el error `no such column: X`
- **Then** el mensaje contiene `«X»` y `"Revisa los nombres de las columnas"`

### SC-03: Columna ambigua
- **Given** una consulta con una columna que existe en más de una tabla sin prefijo
- **When** se genera el error `ambiguous column name: X`
- **Then** el mensaje contiene `"más de una tabla"` y `"Prefija el nombre con la tabla: tabla.X"`

### SC-04: Error de sintaxis (near)
- **Given** una consulta con error de sintaxis
- **When** se genera el error `near "X": syntax error`
- **Then** el mensaje contiene `«X»` y `"Revisa la ortografía del SQL"`

### SC-05: Error de sintaxis general
- **Given** una consulta con error de sintaxis sin token identificable
- **When** se genera el error `syntax error`
- **Then** el mensaje contiene `"Error de sintaxis"` y `"Revisa la consulta"`

### SC-06: Consulta incompleta
- **Given** una consulta que termina abruptamente (sin cerrar paréntesis, etc.)
- **When** se genera el error `incomplete input`
- **Then** el mensaje contiene `"incompleta"` y `"falta un valor"`

### SC-07: Función inexistente
- **Given** una consulta que usa una función no válida
- **When** se genera el error `no such function: X`
- **Then** el mensaje contiene `«X»` y ejemplos `"COUNT, SUM, AVG, MIN, MAX"`

### SC-08: Mismatch de tipos
- **Given** una operación que mezcla tipos incompatibles
- **When** se genera el error `datatype mismatch`
- **Then** el mensaje menciona "texto (TEXT)" y "números (INTEGER/REAL)"

### SC-09: Restricción FK violada
- **Given** una inserción que viola una llave foránea
- **When** se genera `foreign key constraint failed`
- **Then** el mensaje contiene `"llave foránea"`

### SC-10: Restricción general violada
- **Given** una inserción que viola una restricción UNIQUE o NOT NULL
- **When** se genera `constraint failed`
- **Then** el mensaje contiene `"restricción"` y `"campo único o no nulo"`

### SC-11: Error no reconocido
- **Given** un error de SQLite no listado en `_PATTERNS`
- **When** se llama `friendly_error()`
- **Then** retorna `"La base de datos respondió con un error:"` + los primeros 220 chars del error original (sin saltos de línea)

### SC-12: Muestra nombres de tablas (hint)
- **Given** la lista de tablas cargadas `["clientes", "pedidos"]`
- **When** se genera un error de "tabla inexistente"
- **Then** el mensaje menciona las tablas disponibles para ayudar al usuario

## Edge Cases
- Error vacío: retorna fallback genérico
- Error con saltos de línea: `_quote_error` reemplaza por espacios, trunca a 220 chars
- Error con caracteres especiales: se procesa correctamente
- Múltiples coincidencias de patrón: se usa el primero en `_PATTERNS` (orden importa)

## Archivos a tocar
- `core/error_friendly.py` (NO TOCAR — módulo base estable)

## Notas de diseño
- Patrones en minúscula (`low = raw.lower()`) para matching case-insensitive
- `_PATTERNS` es una lista ordenada; el orden define prioridad de matching
- Grupos de captura `(?P<name>...)` o `m.group(1)` extraen el identificador problemático
