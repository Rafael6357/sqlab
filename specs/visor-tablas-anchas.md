# Spec: visor-tablas-anchas

> Estado: APPROVED — bugfix SDD (tabla real de ~200 columnas × 221 filas se ve
> "vacía" en `CONTENIDO DE LA TABLA` y en `RESULTADO DE LA CONSULTA`).

## Causa raíz (confirmada por usuario)
Parseo intacto (un `SELECT` de 4 columnas se ve perfecto). El problema es solo
render: ambas grillas usan `QHeaderView.ResizeMode.Stretch`, así que N columnas
se reparten el ancho a partes iguales (~6 px con 200 columnas) y el QSS
(`QTableWidget::item { padding: 4px 8px }`) recorta todo el texto.

## Objetivo
Tablas anchas legibles con scroll horizontal; tablas angostas sin regresión
(sin huecos raros a la derecha).

## Acceptance criteria (Given/When/Then)
- **VA-01**: Given tabla de 60 columnas, When se muestra en el visor,
  Then el modo del header NO es `Stretch` y la suma de anchos de sección
  supera el ancho del viewport (hay scroll horizontal real).
- **VA-02**: Given celdas con texto, When se inspecciona un item,
  Then su tooltip contiene el valor completo (revela el dato con el mouse).
- **VA-03**: Given tabla angosta (2-3 columnas), When se muestra,
  Then la última columna absorbe el espacio sobrante (`stretchLastSection`).
- **VA-04**: Given valores largos, When se renderizan,
  Then la sección queda topada (máximo 300 px) con elipsis a la derecha.
- **VA-05**: Headers `col ::tipo` del visor y columnas del resultado intactos.

## Edge cases
- Celdas `None` → texto `""` con tooltip `""` (sin crash).
- Valores numéricos mantienen alineación derecha.
- Offscreen: los tests usan anchos de sección, no píxeles de pantalla.

## Límites conocidos
- `ResizeToContents` recorre todas las celdas: con 221×200 puede tardar
  ~1-2 s al cargar/mostrar (una sola vez por operación).
- Sin congelar la primera columna (QTableWidget no lo soporta nativo).

## Requisitos de testing
- `tests/test_visor_tablas.py`: fixture sintético ancho (60 cols × 5 filas,
  sin datos reales), VA-01..VA-05 en visor y resultado.
- `python -m pytest -q` 100 % + build.
