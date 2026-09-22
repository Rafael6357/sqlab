# SPEC: graficos-basicos

## Meta
- **Feature**: graficos-basicos
- **Autor**: opencode (Muse Spark)
- **Fecha**: 2026-09-21
- **Estado**: `APPROVED`

## Objetivo
Botón `GRAFICAR` que dibuja barras o líneas desde el último resultado de
2 columnas (etiqueta, valor) con `PySide6.QtCharts` (paquete `PySide6-Addons`),
en tema oscuro, con exportar a PNG.

## Acceptance Criteria

### GR-01 — botón y diálogo
- **Given** resultado de 2 columnas con la 2ª numérica
- **When** clic `GRAFICAR` (cabecera de resultados)
- **Then** diálogo con gráfico de barras + selector barras/líneas + botón `GUARDAR PNG`.

### GR-02 — validación
- **Given** resultado sin 2 columnas o 2ª columna no numérica
- **When** clic `GRAFICAR`
- **Then** toast `SE NECESITAN 2 COLUMNAS (ETIQUETA, VALOR)`; sin diálogo.

### GR-03 — PNG
- **Given** gráfico visible
- **When** `GUARDAR PNG`
- **Then** fichero `.png` no vacío; cancelar no crea fichero.

### GR-04 — tope de puntos
- **Given** resultado gigante
- **When** graficar
- **Then** se usan las primeras 200 filas (aviso en el título).

### GR-05 — nunca silencioso (diagnóstico visible)
- **Given** QtCharts no cargó o el diálogo falla
- **When** clic `GRAFICAR`
- **Then** toast `GRÁFICOS NO DISPONIBLES: <motivo>` o diálogo con el traceback; jamás silencio (el exe windowed no tiene consola).

## Edge Cases
- [x] Valores `None` en Y: se saltan (no rompen la serie).
- [x] Etiquetas largas: elide en el eje (QtCharts las rota si hace falta).
- [x] Sin resultados: mismo toast de validación.

## Límites Conocidos
- Solo barras y líneas, 2 columnas; sin apilados ni 3D (fuera de alcance).
- Nueva dependencia `PySide6-Addons==6.10.1` (+~165 MB descarga, exe más pesado).

## Archivos a tocar
- `requirements.txt` (`PySide6-Addons==6.10.1`), `run.spec` (`hiddenimports` si hace falta)
- `ui/graficos.py` (nuevo: `datos_para_grafico` puro + `DialogoGrafico`)
- `ui/main_window.py` (botón + `graficar_resultado`)
- `tests/test_graficos.py` (nuevo: GR-01..GR-04)

## Tests requeridos
- **Unit**: mapeo columnas→puntos (nulos saltados, tope 200); validación.
- **E2E**: botón, diálogo con chart, PNG no vacío, toast sin 2 columnas.
- **Nombre de archivos de test**: `tests/test_graficos.py`

## Notas de diseño
- Lógica de datos pura (`datos_para_grafico`) testeable sin pintar.
- Tema oscuro del chart a mano (fondo `#0a1212`, serie `#00ffaa`).
