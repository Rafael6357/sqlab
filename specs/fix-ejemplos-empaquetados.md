# Spec: fix-ejemplos-empaquetados

> Estado: APPROVED — bugfix SDD (reporte: `EJEMPLO NO ENCONTRADO` en el .exe).

## Objetivo
Los botones `EJEMPLO: TIENDA` y `EJEMPLO: BIBLIOTECA` deben funcionar en el
ejecutable empaquetado (`dist/SQLab.exe`, onefile) en **cualquier dispositivo**,
sin depender de archivos externos junto al exe.

## Causa raíz
`MainWindow.cargar_preset` (`ui/main_window.py`) resuelve
`examples/<fichero>` relativo a `os.path.dirname(__file__)/..`. En modo frozen
(onefile) eso cae en la carpeta temporal `_MEIxxxxxx/` de PyInstaller, pero
`run.spec` solo empaqueta `resources/` en `datas` — `examples/` nunca viaja
dentro del exe. En desarrollo funciona porque `app-sql-offline/examples/`
sí existe en disco. Error reportado:
`No se encontró: ...\Temp\_MEI00002ca42\examples\ejemplo_tienda.json`.

## Acceptance criteria (Given/When/Then)
- **EE-01**: Given modo desarrollo, When se resuelve el dir base de recursos,
  Then apunta a `app-sql-offline/` (contiene `examples/ejemplo_tienda.json` y
  `ejemplo_biblioteca.json`).
- **EE-02**: Given modo frozen (`sys.frozen=True`, `sys._MEIPASS=<tmp>`),
  When se resuelve el dir base de recursos, Then devuelve `<tmp>` (raíz del
  bundle, donde PyInstaller extrae `datas`).
- **EE-03**: Given `run.spec`, When se inspecciona `datas`, Then incluye el
  mapeo `app-sql-offline/examples → examples`.
- **EE-04**: Given MainWindow, When `cargar_preset("ejemplo_tienda.json")` y
  `cargar_preset("ejemplo_biblioteca.json")`, Then ambos devuelven `True` y
  cargan sus tablas en el engine.
- **EE-05**: Given el repo, When se lista `examples/csv/`, Then existen
  `productos.csv` y `clientes.csv` (también viajan en el bundle por ser
  subcarpeta de `examples/`).

## Edge cases
- Otro dispositivo sin Python/código: onefile extrae `examples/` a `_MEI...`
  automáticamente al arrancar; solo lectura (suficiente: se cargan en memoria).
- `_MEIPASS` ausente con `frozen=True` (caso anómalo): fallback a ruta dev.
- Nombres con mayúsculas: `load_file` ya es case-insensitive por extensión;
  los ficheros del bundle conservan minúsculas.

## Límites conocidos
- Los ejemplos del bundle son de solo lectura en el exe (no se pueden
  modificar dentro del bundle; el usuario puede guardar sesión aparte).
- No se añade fallback a carpeta externa junto al exe (out of scope).

## Requisitos de testing
- `tests/test_ejemplos_empaquetados.py`: EE-01 (dev), EE-02 (frozen simulado
  con monkeypatch de `sys.frozen`/`sys._MEIPASS`), EE-03 (texto de run.spec),
  EE-04 (ambos presets vía fixture `app`), EE-05 (csvs presentes).
- `python -m pytest -q` 100 % + rebuild `bin/build.ps1` + verificación de que
  `build/run/Analysis-00.toc` lista `examples/ejemplo_tienda.json`.
