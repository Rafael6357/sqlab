# SPEC: consola-vacia-inicial

## Meta
- **Feature**: consola-vacia-inicial
- **Autor**: opencode (Muse Spark)
- **Fecha**: 2026-09-18
- **Estado**: `APPROVED`

## Objetivo
Al abrir la app, la consola SQL aparece vacía (solo placeholder): hoy se
auto-escribe la `defaultQuery` del ejemplo Tienda, que el usuario no pidió.

## Acceptance Criteria

### CV-01 — editor vacío al arrancar
- **Given** arranque limpio
- **When** aparece la ventana
- **Then** el editor no tiene texto (placeholder visible); las tablas del ejemplo Tienda sí se cargan (esquema vivo).

### CV-02 — defaultQuery bajo demanda
- **Given** sesión cargada
- **When** el usuario pulsa un botón/acción explícita de plantilla (o no hay tablas y pide escribir)
- **Then** (sin cambios) el resto del flujo usa `default_query` como hoy al cargar ejercicios posteriores; solo el arranque inicial no escribe.

## Edge Cases
- [x] Sin tablas (carga fallida): editor vacío igual, sin crash.
- [x] QSettings/autocompletado: intactos.

## Límites Conocidos
- El preset Tienda se sigue cargando al inicio (datos de ejemplo inmediatos); solo se deja de inyectar texto.

## Archivos a tocar
- `ui/main_window.py` (`_load_initial_preset`: cargar preset sin `_set_default_query`)
- `tests/test_consola_vacia.py` (nuevo: CV-01)

## Tests requeridos
- **E2E**: `MainWindow` recién creada → `editor.toPlainText() == ""` y tablas Tienda cargadas.
- **Nombre de archivos de test**: `tests/test_consola_vacia.py`

## Notas de diseño
- Cambio mínimo: no llamar a `_set_default_query()` en el arranque; el método sigue para cargas posteriores.
