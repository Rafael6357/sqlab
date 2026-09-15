# SPEC: Template para nuevas funcionalidades

> **Instrucciones**: copiar este archivo como `specs/<feature-id>.md`, rellenar cada sección.
> ID del feature: `kebab-case` (ej. `guardar-sesion`, `notificaciones-toast`).

## Meta
- **Feature**: [nombre corto]
- **Autor**: [quién escribe]
- **Fecha**: [YYYY-MM-DD]
- **Estado**: `DRAFT` | `APPROVED` | `IMPLEMENTED`

## Objetivo
> Describir en 1-2 oraciones qué hace el feature y para qué sirve.

## Acceptance Criteria

### [Criterio 1 — titulo corto]
- **Given** [estado previo]
- **When** [acción del usuario/sistema]
- **Then** [resultado esperado]

### [Criterio 2]
- **Given** ...
- **When** ...
- **Then** ...

*(Agregar tantos criterios como sean necesarios)*

## Edge Cases
- [ ] Caso vacío / sin datos
- [ ] Caso límite de tamaño
- [ ] Caso de error / input inválido
- [ ] Caso de concurrencia (si aplica)

## Límites Conocidos
- Describir limitaciones conocidas que el usuario o desarrollador debe entender

## Archivos a tocar
- Archivos que serán modificados o creados para implementar este feature

## Tests requeridos
- **Unit**: qué funciones/módulos se testean individualmente
- **E2E**: qué flujos completos se verifican
- **Nombre de archivos de test**: `tests/test_<module>.py`, `tests/test_e2e_<feature>.py`

## Notas de diseño
- Decisiones de implementación, trade-offs, alternativas descartadas
- Referencia a `design.md` si hay decisiones arquitectónicas relevantes
