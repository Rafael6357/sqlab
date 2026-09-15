# SPEC: Resaltador de sintaxis SQL

- **Feature**: SQLHighlighter — resaltado de sintaxis SQL en el editor de código
- **Estado**: IMPLEMENTADO (v1+)
- **Archivo**: `ui/sql_highlighter.py` (~80 líneas)
- **Tests**: *(sin tests unitarios dedicados — cubierto indirectamente por E2E)*

## Objetivo
Proveer resaltado de sintaxis SQL en el editor de texto de la app, usando colores de la paleta cyberpunk para keywords, funciones, strings, comentarios, números y operadores.

## Acceptance Criteria

### SC-01: Keywords se resaltan en verde
- **Given** el editor tiene el highlighter instalado
- **When** el usuario escribe `SELECT * FROM clientes WHERE id = 1`
- **Then** las palabras `SELECT`, `FROM`, `WHERE` se resaltan en verde (`#00ffaa`, `KEYWORD_COLOR`), en negrita

### SC-02: Funciones SQL se resaltan en cian
- **Given** el editor tiene el highlighter
- **When** el usuario escribe `COUNT(*)` o `SUM(precio)`
- **Then** `COUNT` y `SUM` se resaltan en cian (`#00e5ff`, `FUNCTION_COLOR`), solo cuando seguidos de `(`

### SC-03: Strings se resaltan en ámbar
- **Given** el editor tiene el highlighter
- **When** el usuario escribe `'Ana'` o `"Madrid"`
- **Then** las cadenas entre comillas simples o dobles se resaltan en ámbar (`#ffb300`, `STRING_COLOR`)

### SC-04: Comentarios SQL se resaltan en gris-verde
- **Given** el editor tiene el highlighter
- **When** el usuario escribe `-- esto es un comentario` o `/* bloque */`
- **Then** el comentario se resaltan en color muted (`#4d7c6d`, `COMMENT_COLOR`), en cursiva

### SC-05: Números se resaltan en ámbar
- **Given** el editor tiene el highlighter
- **When** el usuario escribe `42` o `3.14`
- **Then** los números se resaltan en ámbar (`#ffb300`, `NUMBER_COLOR`)

### SC-06: Operadores se resaltan en verde-dim
- **Given** el editor tiene el highlighter
- **When** el usuario escribe `=`, `<>`, `>`, `<`, `+`, `-`, `*`, `/`
- **Then** los operadores se resaltan en dim (`#00aa70`, `OPERATOR_COLOR`)

### SC-07: Keywords son case-insensitive
- **Given** el highlighter con option `CaseInsensitiveOption`
- **When** el usuario escribe `select`, `Select`, `SELECT`
- **Then** todas las variantes se resaltan igual (keyword verde)

### SC-08: Nombres de tablas/columnas NO se resaltan
- **Given** el editor tiene el highlighter
- **When** el usuario escribe `clientes` o `nombre`
- **Then** esos tokens no se resaltan con ningún color especial (se quedan en el color base del editor)

### SC-09: Función sin paréntesis NO se resalta como función
- **Given** el highlighter
- **When** el usuario escribe `COUNT` sin `(` después
- **Then** `COUNT` se resalta como keyword (verde), no como función (cian)

### SC-10: Keywords y funciones conocidas están completas
- **Given** la lista `KEYWORDS` y `FUNCTIONS`
- **When** se inspeccionan
- **Then** `KEYWORDS` contiene al menos 40 keywords SQL estándar (SELECT, FROM, WHERE, JOIN, GROUP BY, ORDER BY, etc.)
- **Then** `FUNCTIONS` contiene al menos 15 funciones SQL (COUNT, SUM, AVG, MIN, MAX, ROUND, etc.)

## Edge Cases
- Cadena vacía: no crash, retorna sin formato
- Múltiples keywords en una línea: todas se resaltan
- Comentario multilinea `/* ... */`: se maneja correctamente
- String sin cerrar: el regex `.*?` es greedy minimal, puede no resaltar correctamente (conocido)

## Límites Conocidos
- Sin soporte de highlighting multilinea para strings entre comillas (solo inline)
- Sin highlighting de identificadores (nombres de tablas/columnas) — intencional
- Sin highlighting de tipos de datos SQL (INTEGER, TEXT, etc.)

## Archivos a tocar
- `ui/sql_highlighter.py` (se puede agregar keywords/funciones sin cambio estructural)

## Notas de diseño
- `QSyntaxHighlighter` subclass con reglas regex simples (`\b{token}\b`)
- Colores alineados con la paleta de `dark.qss` (verde, cian, ámbar, muted)
- Funciones: regex incluye `(?=\s*\()` para resaltar solo cuando son llamadas
- Sin dependencias externas (solo PySide6)
