# Spec: fix-carga-robusta

> Estado: APPROVED — bugfix SDD (4 bugs de carga con pérdida silenciosa).

## Objetivo
Eliminar pérdidas silenciosas al cargar: JSON con BOM, cabeceras gemelas
por mayúsculas o con comillas, tablas descartadas por el engine sin aviso y
`SELECT *` sin entrecomillar para tablas con espacios.

## Acceptance criteria (Given/When/Then)
- **CR-01**: Given `.json` guardado con BOM (Notepad/Excel Windows),
  When `load_file`, Then carga igual que sin BOM (`utf-8-sig`; también en
  `cargar_sesion`).
- **CR-02**: Given cabeceras `Nombre` + `nombre` (o con `"` como `a"b`),
  When normalizar, Then `Nombre` + `nombre_2` (dedup case-insensitive,
  `"` eliminadas; vacías → `colN` como antes).
- **CR-03**: Given `load_tables` omite una tabla (CREATE/INSERT fallido),
  When termina, Then devuelve la lista de omitidas; `_aplicar_resultado`
  compara esperadas vs cargadas y si hay omitidas muestra toast
  `TABLA(S) OMITIDA(S): <nombres>`.
- **CR-04**: Given tabla `mis datos` (nombre con espacio, válido en JSON),
  When `ver_select_all`, Then editor = `SELECT * FROM "mis datos";`.

## Edge cases
- BOM + formato IA combinados.
- `"` sola como cabecera → `colN`.
- Todo carga bien → sin toasts ni diálogos extra (cero ruido).

## Límites conocidos
- No se validan otros caracteres raros en nombres (SQLite entrecomillado
  los acepta; solo `"` rompía el CREATE).

## Requisitos de testing
- `tests/test_fix_carga_robusta.py`: CR-01..CR-04 (unit + E2E con `app`).
- `python -m pytest -q` 100 % + build.
