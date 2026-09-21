# SPEC: historial-contraido

## Meta
- **Feature**: historial-contraido
- **Autor**: opencode (Muse Spark)
- **Fecha**: 2026-09-18
- **Estado**: `APPROVED`

## Objetivo
El `HISTORIAL DE CONSULTAS` aparece contraído por defecto (toggle
`VER_HISTORIAL`, patrón de la pista): la matriz queda despejada y el
historial se expande a demanda.

## Acceptance Criteria

### HC-01 — contraído al arrancar
- **Given** arranque o carga nueva
- **When** se mira la matriz
- **Then** el toggle existe, está sin marcar (`VER_HISTORIAL`) y la lista está oculta.

### HC-02 — expandir/contraer
- **Given** toggle
- **When** clic
- **Then** la lista se muestra (`OCULTAR_HISTORIAL`) / se oculta (`VER_HISTORIAL`).

### HC-03 — funciones intactas
- **Given** historial con entradas (lista oculta o visible)
- **When** clic en entrada / `[LIMPIAR]`
- **Then** recarga+ejecuta / limpia, igual que hoy.

## Edge Cases
- [x] Ejecutar consulta con lista oculta: el historial se actualiza (se ve al expandir).
- [x] `[LIMPIAR]` visible siempre (no depende del toggle).

## Límites Conocidos
- Solo colapso visual (`setVisible`); sin animación.

## Archivos a tocar
- `ui/paneles.py` (`_build_matrix`: toggle + visibilidad inicial)
- `ui/main_window.py` (`_on_historial_toggle`, conectar en `_connect_signals`)
- `tests/test_historial_contraido.py` (nuevo: HC-01..HC-03)

## Tests requeridos
- **E2E**: toggle existe/apagado/lista oculta; clic expande/contrae; limpiar y recarga intactos.
- **Nombre de archivos de test**: `tests/test_historial_contraido.py`

## Notas de diseño
- Mismo patrón que `pista_toggle`/`pista_card` (checkable, `checked=False`).
