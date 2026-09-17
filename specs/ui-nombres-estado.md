# Spec: ui-nombres-estado

> Estado: APPROVED — renombres UI + barra de estado real + arranque maximizado.

## Objetivo
Textos visibles en español claro de principiante (sin jerga `NODO/MATRIZ/
VOLCADO/TRANSACCIONES/IA_DESCIFRADO`), barra de estado con datos reales en
vez de etiquetas decorativas, y arranque maximizado.

## Renombres (solo texto visible; `objectName` y atributos internos intactos)
| Actual | Nuevo |
|---|---|
| `TABLAS` | `CARGAR TABLAS` |
| `VOLCADO DE TABLA` (tab) | `CONTENIDO DE LA TABLA` |
| `> REGISTRO DE TRANSACCIONES` | `> HISTORIAL DE CONSULTAS` |
| `> MATRIZ DE ESQUEMA` | `> ESQUEMA DE TABLAS` |
| `>> MATRIZ DE RESULTADOS` | `>> RESULTADO DE LA CONSULTA` |
| `[DIRECTIVA DE MISIÓN]` (tab) | `[EJERCICIO]` |
| `FORMATO` | `FORMATO SQL` (no checkable, spec `formato-sql-real`) |
| `SAV` / `SES` | `GUARDAR SESIÓN` / `CARGAR SESIÓN` |
| `AC` (checkbox) | `AUTOCOMPLETAR` |
| `[IA_DESCIFRADO]` + `PROTOCOLO DE SUGERENCIA:` | `PISTA:` (un solo label `PISTA:`) |
| `NODO:` | `TABLA ACTIVA:` |
| `0 REGISTRO(S)` / `N REGISTRO(S)` | `0 REGISTROS` / `N REGISTROS` |
| `MEMORIA: OK` | `EN MEMORIA` |
| `FORMATO JSON IA` | `PLANTILLA JSON PARA IA` |
| hint error `...en la MATRIZ DE ESQUEMA...` | `...en ESQUEMA DE TABLAS...` |
| tooltip TABLAS | documenta ARCHIVOS (multi) + CARPETA |
| tooltip FORMATO | `Aplica formato SQL estándar: mayúsculas, saltos por cláusula e indentación` |

## Barra de estado real (reemplaza `CACHÉ_TX`/`PRAGMA` decorativos)
- **UN-01**: el `HBox` con `CACHÉ_TX: SINCRONIZADA` / `PRAGMA: DESACTIVADO`
  se sustituye por un único `QLabel status_db` (`StatusLabel`):
  `TABLAS: N · FILAS: M · DB: MEMORIA OK`.
- **UN-02**: `_refresh_status()` se llama en `_aplicar_resultado` y tras cada
  `ejecutar_consulta` (éxito o error; los conteos reflejan el engine).

## Arranque maximizado
- **UN-03**: `app.py` usa `window.showMaximized()` (mantiene `resize` previo
  como tamaño fallback).

## Edge cases / límites
- Textos más largos (`GUARDAR SESIÓN`, `AUTOCOMPLETAR`…): el HUD usa layout
  con stretches; sin anchos fijos nuevos (salvo existentes).
- Tests E2E que asertaban textos viejos se actualizan en el mismo cambio.

## Requisitos de testing
- `tests/test_ui_nombres.py`: cada texto nuevo presente, cada texto viejo
  ausente (barrido de widgets), `status_db` con formato y actualización tras
  carga y tras ejecución, `showMaximized` en `app.py`.
- `python -m pytest -q` 100 % + build.
