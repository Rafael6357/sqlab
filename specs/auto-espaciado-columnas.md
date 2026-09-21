# SPEC: auto-espaciado-columnas

## Meta
- **Feature**: auto-espaciado-columnas
- **Autor**: opencode (Muse Spark)
- **Fecha**: 2026-09-18
- **Estado**: `APPROVED`

## Objetivo
Al mostrar un resultado, cada columna mide lo que necesita su contenido
(nombre de columna completo siempre visible, tope 300 px); al estirar el
panel, las columnas crecen proporcionalmente a ese ancho base. Adiós a
columnas recortadas y a huecos muertos.

## Acceptance Criteria

### AE-01 — nombres completos al mostrar
- **Given** resultado con columnas de cualquier ancho
- **When** se pinta
- **Then** cada sección mide contenido (cabecera + muestra, tope 300 px): ningún nombre de columna queda recortado por estrechez inicial.

### AE-02 — crecimiento proporcional al estirar
- **Given** grilla pintada con anchos base
- **When** el panel se ensancha (splitter/ventana)
- **Then** el hueco extra se reparte entre columnas en proporción a sus anchos base (no solo la última, no a partes iguales ciegas).

### AE-03 — angostas sin huecos, anchas con scroll
- **Given** tabla angosta (total < viewport) / ancha (total > viewport)
- **When** se pinta
- **Then** angosta: sin hueco morto a la derecha; ancha: scroll horizontal real (sin `Stretch` global).

## Edge Cases
- [x] 200 columnas: el reparto proporcional no recorre celdas, solo anchos (O(cols)).
- [x] Contenido larguísimo: tope 300 px + elipsis + tooltip (intacto).
- [x] Usuario reajusta a mano: su ajuste es la nueva base para repartos futuros.

## Límites Conocidos
- El reparto usa anchos base medidos (aprox. por muestreo, spec rendimiento); no mide celdas fuera de muestra.
- `setSectionResizeMode(Stretch)` reparte a partes iguales: por eso se implementa reparto manual proporcional en `resizeEvent` del panel.

## Archivos a tocar
- `ui/tablas.py` (`repartir_anchos_proporcional`, ajuste de `_ajustar_anchos` para medir cabecera completa)
- `ui/main_window.py` (conectar reparto al resize del panel de resultados/visor)
- `tests/test_auto_espaciado.py` (nuevo: AE-01..AE-03)

## Tests requeridos
- **Unit/E2E**: cabecera larga no recortada; suma de anchos tras reparto = viewport (tolerancia); angosta sin hueco; ancha con scroll.
- **Nombre de archivos de test**: `tests/test_auto_espaciado.py`

## Notas de diseño
- `_ajustar_anchos` ya mide cabecera + muestra: AE-01 exige además que la cabecera NUNCA se mida por debajo de su texto completo (hoy podría, si `horizontalAdvance` + 20... no: ya suma header; el bug real es el reparto al estirar).
- Reparto: instalar `eventFilter` o subclasear resize del `QTableWidget`? Opción elegida: `eventFilter` en MainWindow para `resultado_tabla`/`visor_tabla` (`QEvent.Resize`) que re-escala secciones según base guardada en propiedad.
- Base guardada: tras cada pintado, `grilla.setProperty("anchos_base", [...])`; el usuario al reajustar actualiza la base (señal `sectionResized`).
