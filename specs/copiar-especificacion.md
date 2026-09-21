# SPEC: copiar-especificacion

## Meta
- **Feature**: copiar-especificacion
- **Autor**: opencode (Muse Spark)
- **Fecha**: 2026-09-18
- **Estado**: `APPROVED`

## Objetivo
Botón `COPIAR` en la tarjeta `ESPECIFICACIÓN DE CONSULTA` que copia al
portapapeles el título + enunciado + columnas objetivo (+ orden si hay).

## Acceptance Criteria

### CE-01 — copia completa
- **Given** ejercicio cargado con enunciado
- **When** clic `COPIAR`
- **Then** el portapapeles trae título, enunciado y `COLUMNAS OBJETIVO: ...` (+ orden si `sort_label` visible); toast `ESPECIFICACIÓN COPIADA`.

### CE-02 — sin ejercicio
- **Given** sin ejercicio (`SIN EJERCICIO`)
- **When** clic `COPIAR`
- **Then** toast `SIN EJERCICIO // NADA QUE COPIAR`, portapapeles intacto.

## Edge Cases
- [x] Sin columnas objetivo: se copia título + enunciado.
- [x] Enunciado largo con tildes: UTF-8 intacto.

## Límites Conocidos
- Copia texto plano (no incluye la consulta del editor; eso es COPIAR PARA IA).

## Archivos a tocar
- `ui/main_window.py` (`_build_mission_tab`: botón + `copiar_especificacion`)
- `tests/test_copiar_especificacion.py` (nuevo: CE-01/CE-02)

## Tests requeridos
- **E2E**: portapapeles con partes; sin ejercicio → toast y sin cambios.
- **Nombre de archivos de test**: `tests/test_copiar_especificacion.py`

## Notas de diseño
- Patrón `copiar_consulta` (QGuiApplication.clipboard + toast).
