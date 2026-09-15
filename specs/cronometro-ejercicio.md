# SPEC: Cronómetro y temporizador por ejercicio

## Meta
- **Feature**: cronómetro / temporizador por ejercicio
- **Autor**: Rafael
- **Fecha**: 2026-09-15
- **Estado**: `APPROVED`

## Objetivo
Permitir al usuario activar en el HUD un **cronómetro** (cuenta hacia arriba) o un **temporizador**
(cuenta regresiva desde N segundos configurables) para medir si resuelve cada ejercicio bajo
presión de tiempo. Al cargar o reajustar un ejercicio, el cronómetro se resetea y se detiene.

## Acceptance Criteria

### CR-01 — Control visible en el HUD
- **Given** la ventana principal abierta
- **When** se observa la barra superior (`TitleBar`)
- **Then** existe un marco `CronoFrame` con: etiqueta `CronoTime` (`00:00:00`), toggle de modo
  `CronoMode` (`CRONO`/`TEMPO`), botón `CronoStart` (`INICIAR`/`PAUSAR`), botón `CronoReset`
  (`REINICIAR`) y spin `CronoSpin` (solo visible en modo `TEMPO`)

### CR-02 — Cronómetro cuenta hacia arriba
- **Given** modo `CRONO` y cronómetro detenido en `00:00:00`
- **When** el usuario pulsa `INICIAR`
- **Then** `CronoTime` avanza cada segundo (`00:00:01`, `00:00:02`, …) y el botón pasa a `PAUSAR`;
  al pulsar `PAUSAR` el valor se congela

### CR-03 — Temporizador cuenta regresiva
- **Given** modo `TEMPO` con N segundos en `CronoSpin` (5–3600)
- **When** el usuario pulsa `INICIAR`
- **Then** `CronoTime` baja en `HH:MM:SS` desde N hasta `00:00:00`; al llegar a cero el
  temporizador se detiene, `CronoTime` entra en estado de alerta roja y se muestra
  el toast `TIEMPO AGOTADO`

### CR-04 — Reinicio manual
- **Given** cronómetro en marcha o pausado con valor distinto de cero
- **When** el usuario pulsa `REINICIAR`
- **Then** `CronoTime` vuelve a `00:00:00` (modo `CRONO`) o a N (modo `TEMPO`), el estado
  de alerta se limpia y el cronómetro queda detenido

### CR-05 — Reset automático al cambiar de ejercicio
- **Given** cronómetro en marcha con valor acumulado
- **When** se carga un ejercicio nuevo (preset, JSON, sesión, CSV) o se restablecen los datos
- **Then** `_aplicar_resultado` reinicia el cronómetro (valor a cero/base, detenido, alerta limpia)

## Edge Cases
- [x] Cambiar de modo (`CRONO`/`TEMPO`) en marcha detiene y reinicia el crono
- [x] Editar `CronoSpin` en marcha detiene y reinicia el crono
- [x] `CronoSpin` limita el rango a 5–3600 segundos (sin valores fuera de rango)
- [x] Temporizador con N ya consumido y `REINICIAR` restaura N, no cero
- [x] Carga de ejercicio fallida (`result.ok == False`) NO reinicia el crono
- [x] Display limitado a `HH:MM:SS` (tope `99:59:59`)

## Límites Conocidos
- Sin persistencia: el estado del crono no se guarda en sesiones ni sobrevive al cierre.
- Granularidad de 1 segundo (tics de `QTimer` de 1000 ms), compensados con `time.monotonic`
  para evitar deriva.
- El crono no detecta "ejercicio resuelto": lo detiene manualmente el usuario.

## Archivos a tocar
- `ui/main_window.py` — `_build_hud` (frame), `_start_timers` (QTimer dedicado),
  métodos `_crono_*`, reset en `_aplicar_resultado`
- `resources/dark.qss` — estilos `CronoFrame/CronoTime/CronoMode/CronoSpin/alerta`
- `tests/test_cronometro.py` — tests E2E (nuevo módulo)
- `tests/conftest.py` — mapear `test_cronometro` → spec `cronometro-ejercicio`

## Tests requeridos
- **E2E** (`tests/test_cronometro.py`, qtbot offscreen): CR-01 a CR-05, más formato
  (unit de `_format_crono`) y ticks unitarios sin esperas reales
- Nombres: `test_cronometro.py`; marca automática `spec('cronometro-ejercicio')` vía `conftest.py`

## Notas de diseño
- El HUD tiene 40 px fijos; el frame crono es compacto (fuente mono 11 px) para no
  desbordar con los botones existentes.
- Paleta cyber fósforo vigente (verde `#00ffaa`, rojo alerta `#ff3366`); 100 % español.
- Estado de alerta vía dynamic property `alerta` + repolish (patrón Qt en dark-only QSS).
