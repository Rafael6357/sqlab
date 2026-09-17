# Spec: rendimiento-tablas-grandes

> Estado: APPROVED — feature SDD (un CSV mucho más grande que el actual
> ~200 cols × 221 filas congelaría la app: widgets por celda sin tope,
> `fetchall()` total, `INSERT` fila por fila, sin pre-aviso).

## Objetivo
Tablas grandes (≥100k filas o ≥50 MB) cargan sin congelar ni cerrar la app:
render acotado con aviso, medición muestreada, carga por lotes y confirmación
previa por tamaño.

## Constantes (atributos de clase, tunables)
- `VISOR_MAX_FILAS = 2000` (visor `CONTENIDO DE LA TABLA`).
- `RESULTADO_MAX_FILAS = 5000` (grilla de resultados).
- `MUESTRA_MEDICION = 100` (filas para calcular anchos).
- `AVISO_MB = 50` (diálogo de confirmación por tamaño de archivo).

## Acceptance criteria (Given/When/Then)
- **RG-01**: Given tabla de 2500 filas, When se muestra en el visor,
  Then `rowCount() == 2000` y `row_count_label` = `2500 REGISTROS (MOSTRANDO 2000)`.
- **RG-02**: Given resultado de 6000 filas, When se muestra,
  Then grilla con 5000 filas, badge `6000 FILAS` y toast
  `CONSULTA OK: 6000 FILA(S) (MOSTRANDO 5000)`.
- **RG-03**: Given tabla ≤ topes, When se muestra, Then comportamiento
  intacto (labels y badge sin sufijos).
- **RG-04**: Given tabla de 5000 filas × 10 cols, When se ajustan anchos,
  Then el ancho se calcula solo con las primeras 100 filas + cabecera
  (modo `Interactive`, tope 300 px, última columna absorbe hueco).
- **RG-05**: Given archivo > 50 MB en CARGAR TABLAS/CARPETA/EJERCICIO,
  When se elige, Then diálogo de confirmación
  (`ARCHIVO GRANDE: X MB — PUEDE TARDAR`, `[CARGAR]`/`[CANCELAR]`); cancelar
  no carga nada.
- **RG-06**: Given CSV de 5000 filas, When `load_tables`,
  Then todas las filas en BD (vía `executemany`, fallback fila por fila si
  el lote falla, misma semántica de omitir tablas inválidas).

## Edge cases
- Tablas vacías / 1 fila: sin sufijos, sin diálogos.
- `None` en celdas: tooltip `""`, texto `""` (intacto).
- Cancelar en confirmación: sin toasts ni cambios en el engine.
- Diálogo de confirmación mockeable en tests (helper `_confirmar_archivo_grande`).

## Límites conocidos
- El parseo sigue siendo en memoria (sin streaming): un CSV de ~500 MB
  puede agotar RAM — el aviso de 50 MB lo anticipa pero no lo impide.
- `ResizeToContents` se abandona por `Interactive` + muestreo: el ancho es
  aproximado (suficiente con tooltips de valor completo).
- `executemany` acelera el caso limpio; filas inválidas caen al fallback
  lento (igual que antes).

## Requisitos de testing
- `tests/test_rendimiento.py`: RG-01..RG-06 (fixtures sintéticos, sin datos
  reales; sin asserts de tiempo).
- Suite existente intacta (`test_visor_tablas` VA-01..VA-05 deben seguir
  verdes con el nuevo ajuste por muestreo).
- `python -m pytest -q` 100 % + build.
