# Spec: formato-sql-real

> Estado: APPROVED — feature SDD (el botón `FORMATO` solo ponía keywords en
> mayúsculas y su toggle quedaba marcado para siempre).

## Objetivo
El botón (renombrado a `FORMATO SQL`, ver spec `ui-nombres-estado`) aplica un
**formateo real**: keywords en MAYÚSCULAS + **salto de línea antes de cada
cláusula principal** + **indentación** (2 espacios por nivel, subconsultas
anidadas +1 nivel). Mantiene la protección de literales y comentarios de v10
(state machine: `'...'`, `"..."`, `--`, `/* */` intactos).

## Acceptance criteria (Given/When/Then)
- **FS-01**: Given `select a, b from t where x=1 order by a`,
  When formatear, Then:
  `SELECT a, b\nFROM t\nWHERE x = 1\nORDER BY a` (cláusulas compuestas
  `GROUP BY`/`ORDER BY` en una línea).
- **FS-02**: Given subconsulta `select * from (select id from t where n>0) as s`,
  When formatear, Then el bloque interior va indentado un nivel.
- **FS-03**: Given literales `'O''Brien'`, `"col"`, `-- comentario`, `/* x */`,
  When formatear, Then se conservan byte por byte (sin mayúsculas dentro ni
  saltos inyectados).
- **FS-04**: Given texto ya formateado, When formatear de nuevo,
  Then idempotente (mismo resultado).
- **FS-05**: Given clic en el botón, When termina, Then es **botón normal
  (no checkable)**, toast `SINTAXIS SQL FORMATEADA AL ESTÁNDAR`.
- **FS-06**: Cláusulas soportadas: `SELECT FROM WHERE GROUP BY HAVING ORDER BY
  LIMIT OFFSET JOIN* UNION [ALL] VALUES SET` (+ `ON`/`AND`/`OR` indentados
  bajo su cláusula, sin salto propio salvo legibilidad: `AND`/`OR` con salto
  + indentación extra).

## Edge cases
- Editor vacío → no hace nada (sin toast de éxito).
- `;` final se conserva; múltiples sentencias se formatean en secuencia.
- Paréntesis de funciones (`COUNT(*)`) no generan nivel extra (solo `SELECT`
  tras `(` abre nivel).
- Palabras que contienen keywords (`selección`, `fromage`) no se tocan
  (tokenización por palabra completa, como v10).

## Límites conocidos
- No es sqlparse/pg_format: sin alineación de columnas ni reescritura
  semántica; formato legible, no canónico de industria.
- Sin dependencias externas (convención AGENTS.md).

## Requisitos de testing
- `tests/test_formato_sql.py`: unit por cláusula (FS-01/02/06), literales y
  comentarios (FS-03), idempotencia (FS-04), vacío, botón no checkable + aplica
  en editor (E2E con fixture `app`).
- `python -m pytest -q` 100 % + build.
