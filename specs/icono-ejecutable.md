# SPEC: Icono del ejecutable (logo de la app)

## Meta
- **Feature**: icono del ejecutable
- **Autor**: Rafael
- **Fecha**: 2026-09-15
- **Estado**: `APPROVED`

## Objetivo
Que `dist\SQLab.exe` muestre el logo de la app (`resources/logo_sqllab.svg`) como icono
del archivo en Windows, en lugar del icono por defecto de PyInstaller.

## Acceptance Criteria

### IC-01 — ICO multi-tamaño versionado
- **Given** el logo `resources/logo_sqllab.svg`
- **When** se ejecuta `python bin/make_icon.py` (desde la raíz del repo)
- **Then** se genera `app-sql-offline/resources/logo_sqllab.ico` con entradas PNG
  embebidas de 16/24/32/48/64/128/256 px, válido (magic `00 00 01 00`, 7 imágenes)

### IC-02 — Spec de build referencia el icono
- **Given** `run.spec` en la raíz del repo
- **When** se inspecciona el bloque `EXE()`
- **Then** contiene `icon=` apuntando a `app-sql-offline/resources/logo_sqllab.ico`

### IC-03 — Build conserva tema y logo
- **Given** el `.ico` versionado y `run.spec` con `icon=`
- **When** se ejecuta `bin\build.ps1`
- **Then** `dist\SQLab.exe` se genera sin errores, lleva el icono embebido y al
  arrancar muestra tema oscuro + logo (verificación con archive_viewer + arranque real)

## Edge Cases
- [x] SVG con gradientes/filtros: el render `QSvgRenderer` a 256 px produce el bitmap
  fuente (el resto son reescalados Lanczos)
- [x] Reejecutar `make_icon.py` es idempotente (salida determinista)
- [x] Sin Pillow ni deps nuevas: solo PySide6 (`QtSvg`) + stdlib (`struct`, `io`)

## Límites Conocidos
- El `.ico` generado se versiona en git (binario, ~tamaño PNG×7) para que el build
  sea reproducible sin regenerar.
- El icono de ventana en runtime sigue siendo el SVG (`app.py`, `MainWindow`); el `.ico`
  solo afecta al icono del archivo `.exe` en Windows.
- No se incluyen variantes claras del logo (solo modo oscuro, por convención).

## Archivos a tocar
- `bin/make_icon.py` — generador SVG → ICO (nuevo)
- `app-sql-offline/resources/logo_sqllab.ico` — artefacto generado (versionado)
- `run.spec` — `icon=` en `EXE()`
- `tests/test_icono.py` — validación del ICO + referencia en spec (nuevo módulo)
- `tests/conftest.py` — mapear `test_icono` → spec `icono-ejecutable`

## Tests requeridos
- **Unit** (`tests/test_icono.py`): el `.ico` existe, magic y conteo de imágenes OK,
  `run.spec` contiene la ruta del icono y el archivo referenciado existe

## Notas de diseño
- Entradas PNG embebidas en el ICO (soportado desde Windows Vista); tamaños estándar
  16–256 cubren Explorer, taskbar y Alt-Tab.
- `datas` de `run.spec` ya empaqueta todo `resources/`; el `.ico` viaja también en el
  bundle sin cambios extra.
