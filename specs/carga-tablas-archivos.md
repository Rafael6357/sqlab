# Spec: carga-tablas-archivos

> Estado: APPROVED — feature SDD (reporte: el diálogo `TABLAS` no muestra
> archivos `.csv`; era selector de carpetas `getExistingDirectory`).

## Objetivo
El botón `CARGAR TABLAS` permite elegir **archivos sueltos con
multi-selección** (`*.csv`, `*.xlsx`, `*.xls`) ADEMÁS de mantener la carga por
carpeta. Al pulsar el botón se ofrece mini-diálogo custom `[ARCHIVOS]` /
`[CARPETA]` (coherente con `_show_custom_dialog`, sin `QMessageBox`).

## Acceptance criteria (Given/When/Then)
- **CA-01**: Given clic en `CARGAR TABLAS`, When el usuario elige `ARCHIVOS`,
  Then se abre `getOpenFileNames` con filtro
  `Tablas (*.csv *.xlsx *.xls)` + `Todos (*.*)` y multi-selección.
- **CA-02**: Given N archivos elegidos, When se cargan, Then
  `core.session_loader.combinar_resultados([load_file(f)...])` fusiona tablas
  y errores; `_aplicar_resultado` carga en el engine.
- **CA-03**: Given 2+ archivos con el **mismo nombre de tabla** (p. ej.
  `a.csv` + `a.xlsx`), When se combinan, Then **gana el último archivo**
  (orden alfabético de ruta) + toast `TABLA «a» REEMPLAZADA POR ÚLTIMO ARCHIVO`.
- **CA-04**: Given un archivo inválido entre varios válidos, When se combinan,
  Then las tablas válidas se cargan igual y los errores se muestran en el
  diálogo `ERROR DE DECODIFICACIÓN` con el nombre del fichero.
- **CA-05**: Given clic en `CARGAR TABLAS` → `CARPETA`, When se elige carpeta,
  Then comportamiento actual intacto (`load_tablas_folder`).
- **CA-06**: Given cancelar cualquier diálogo, When no hay selección,
  Then no pasa nada (sin diálogos ni toasts).

## Edge cases
- 0 archivos (cancelar) → retorno silencioso.
- Todos inválidos → solo diálogo de errores, sin tocar el engine.
- `result.ejercicio`: se conserva el primero no vacío (archivos sueltos no
  traen ejercicio; el briefing queda `SIN EJERCICIO`).
- Mayúsculas en extensión (`DATOS.CSV`) → `load_file` ya es case-insensitive.

## Límites conocidos
- Sin validación cruzada de esquemas entre archivos (cada tabla es
  independiente, igual que en carpeta).
- Límite práctico ~50k filas por tabla (heredado de design.md).

## Requisitos de testing
- `tests/test_carga_archivos.py`: combinar csv+xlsx (unit con tmp), last-wins
  + lista `reemplazadas`, errores por fichero sin bloquear válidos, todos
  inválidos → `ok=False`, filtro del diálogo documentado, carpeta intacta.
- `python -m pytest -q` 100 % + build.
