# Spec: exportar-resultado-csv

> Estado: APPROVED — feature SDD (caso médico real: analizar el resultado
> fuera de la app; hoy solo se puede copiar a IA o mirar la grilla topada).

## Objetivo
Botón `EXPORTAR CSV` en la cabecera de `RESULTADO DE LA CONSULTA` que guarda
el resultado completo (todas las filas, aunque la grilla esté topada) en un
`.csv` legible por Excel.

## Acceptance criteria (Given/When/Then)
- **EX-01**: Given resultado visible, When clic `EXPORTAR CSV`,
  Then `getSaveFileName` (`CSV (*.csv)`, sugerido `resultado.csv`).
- **EX-02**: Given 6000 filas de resultado (grilla topada en 5000),
  When exportar, Then el fichero trae cabecera + las 6000 filas.
- **EX-03**: Given valores `None`, When exportar, Then celdas con el texto
  `NULL` (enmendado por spec `mostrar-null-en-grillas`: antes celdas vacías).
- **EX-04**: Given fichero exportado, When abrirlo, Then codificación
  `utf-8-sig` (Excel muestra tildes) y delimitador `,`.
- **EX-05**: Given cancelar el diálogo, When vuelve, Then sin fichero,
  sin toast, sin crash.
- **EX-06**: Given sin resultados (standby/error/vacío), When clic,
  Then toast `SIN RESULTADOS // NADA QUE EXPORTAR` (sin diálogo).

## Edge cases
- Resultado de 1 fila / 1 columna.
- Valores con comas, comillas o saltos → entrecomillado CSV estándar
  (`csv.writer` `QUOTE_MINIMAL`).
- Sobrescribir existente: lo decide el diálogo nativo.

## Límites conocidos
- Exporta el último resultado ejecutado (no el visor de tabla).
- Sin selección de delimitador (siempre `,`, como la carga clásica).

## Requisitos de testing
- `tests/test_exportar_csv.py`: EX-01..EX-06 (diálogos mockeados).
- `python -m pytest -q` 100 % + build.
