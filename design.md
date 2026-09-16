# design.md

## Decisión: SQLite en memoria (:memory:)

Toda la sesión vive en `sqlite3.connect(":memory:")`. Cargar un ejercicio recrea la BD. La ejecución es instantánea y 100% offline.

## Trade-offs aceptados
- Sin persistencia automática: al cerrar la app se pierde el estado, salvo que el usuario use *Guardar sesión* (exporta un `.json` con tablas + enunciado + historial).
- Sin merge de esquemas: cada carga reemplaza por completo las tablas anteriores.
- Límite práctico: ~50k filas por tabla; más allá puede degradar la grilla `QTableWidget`.

## Alternativas descartadas
- SQLite en archivo: complica permisos y empaquetado del .exe.
- DuckDB / Postgres embebido: dependencias nativas adicionales, overkill para ejercicios de principiante.

## UI: solo oscuro, pista colapsada, autocompletado OFF
- `dark.qss` único, sin toggle de tema. Paleta cyber fósforo (v5, esquinas rectas,
  scrollbars 4px): black `#040707` · obsidian `#080d0d` · panel `#0a1212` ·
  card `#0f1b1b` · borde `#153330` · verde `#00ffaa` · dim `#00aa70` ·
  ámbar `#ffb300` · cian `#00e5ff` · rojo `#ff3366` · texto `#d7ffec` · muted `#4d7c6d`.
  Solo monoespaciadas del sistema (sin Google Fonts/FontAwesome CDN).
- `QToolButton` para la pista (`checked=False` por defecto) para no distraer.
- `QSettings` guarda el toggle de autocompletado (`false` por defecto, checkbox `AC`
  en la consola). Cuando está activo, `QCompleter` sugiere tablas/columnas/keywords.

## UI SQLab (v8 — diseño vigente sep-2026; app 100 % en español)
La app se llama **SQLab**. HUD minimalista: logo (chip 26px renderizado desde
`resources/logo_sqllab.svg`) + marca `SQLab` + botones (`FORMATO JSON IA`,
`CARGAR EJERCICIO`, CSV/SAV/SES). Sin textos de versión/motor/heap,
sin reloj/ticks, sin testigos T1/T2/IO, sin tarjeta IA Link, sin ASCII-art.
- **Banner de misión**: `[NIVEL]: PRINCIPIANTE ★☆☆` (dificultad tal cual, en mayúsculas) +
  `[MISIÓN]: título` + `VER_PISTA/OCULTAR_PISTA` + `EJEMPLO: TIENDA/BIBLIOTECA`.
- **Hint drawer** oculto por defecto: `[IA_DESCIFRADO] PROTOCOLO DE SUGERENCIA:` + `[CERRAR]`.
- **Matriz de esquema 288px**: nodos `> tabla [NF]`, inspector `NODO: / COLUMNAS` con filas
  `# col [TIPO→[PK]]` (clic inyecta columna), `INSERTAR SELECT *`, `REGISTRO DE
  TRANSACCIONES` (20, `> query`, clic recarga+ejecuta, `[LIMPIAR]`) y barra
  `CACHÉ_TX: SINCRONIZADA / PRAGMA: DESACTIVADO`.
- **Centro 40/60**: tabs `[DIRECTIVA DE MISIÓN]` (spec + OBJETIVO N.º, COLUMNAS OBJETIVO
  en chips verde/cian, ORDEN) y `VOLCADO DE TABLA` (cabeceras `col ::tipo`,
  `N REGISTRO(S)`, `MEMORIA: OK`); consola con `FORMATO` (toggle checkable que
  queda marcado al activarse, `#FormatBtn:checked`), `AC`, `COPIAR PARA IA`
  (`CyberBtn` borde verde), `EJECUTAR_SQL` (F5/Ctrl+Enter), editor + tira
  (punto parpadeante, `LÍN/COL`, `DIALECTO: SQLITE3`, `UTF-8 // CRLF`); matriz
  `>> MATRIZ DE RESULTADOS` con badge `N FILAS`, `T_EJEC: ms // ESTADO: 200 OK` /
  `EN ESPERA` / `FALLO_EJEC // ERROR`, standby limpio y
  `EXCEPCIÓN_SINTAXIS_SQLITE CÓD_ERROR: 0x22` + `CONSEJO DE RECUPERACIÓN` vía
  `error_friendly`.
- **Tooltips** en botones, listas, editor, tabs y grillas (atributo `toolTip` en cada widget).
- **Esquina de grilla**: el botón de esquina de `QTableWidget` se pinta oscuro
  (`QTableCornerButton::section` en `dark.qss`); sin él Qt lo deja blanco (ver bug imagen).
- **Diálogos custom**: `_show_custom_dialog(parent, title, msg, kind)` reemplaza a
  `QMessageBox` (diálogo modal dark con `ACEPTAR`); regla `QMessageBox` eliminada del QSS.
- **Modal JSON**: `ESPECIFICACIÓN DE PROTOCOLO JSON PARA IA` con `COPIAR PLANTILLA`;
  al copiar el botón pasa a `✓ COPIADA` (deshabilitado) y muestra toast `ToastLabel` in-dialog ~2,4 s.
- `COPIAR PARA IA` usa la plantilla misión + query + mejora (en español).
- **Logo**: `resources/logo_sqllab.svg` (SVG Matrix verde, 1200×1200) → ícono de ventana
  (`QIcon`) en `app.py`/`MainWindow` y chip HUD; con Qt se renderiza vía `QIcon`, sin CDN.
  El icono del archivo `.exe` en Windows se genera con `bin/make_icon.py`
  (SVG → `logo_sqllab.ico` multi-tamaño 16–256) y se referencia con `icon=` en `run.spec`.
- **Crono por ejercicio** (v13, v14 verdoso): frame compacto `CronoFrame` en el HUD (`TitleBar`) con
  display `CronoTime` (`HH:MM:SS`), toggle de modo `CronoMode` (`CRONO` cuenta arriba /
  `TEMPO` cuenta regresiva desde `CronoSpin` 5–3600 s), `INICIAR`/`PAUSA` y `REINICIAR`.
  Reset automático (detenido, sin alerta) al aplicar un ejercicio nuevo. Fin de cuenta
  regresiva → toast `TIEMPO AGOTADO` + alerta roja (`#ff3366`). Granularidad 1 s con base
  `time.monotonic`. Sin persistencia del crono. v14: `CronoMode:checked` pasa de ámbar
  (`#ffb300`) a verde (`#00ffaa`/`rgba(0,255,170,0.15)`, como `FormatBtn:checked`) para estética
  verdosa uniforme del HUD.
- **Splitter matriz/editor** (v14): `work_splitter` (`QSplitter` horizontal editor|matriz) con
  `setChildrenCollapsible(False)`, `setCollapsible(0/1,False)`, `editor_pane` 220 / `output_pane`
  240 mínimos, `handleWidth` 6 (QSS `QSplitter::handle:horizontal` 1px visual + `margin:0 2px`
  para hit-area), método `_reset_work_splitter` por doble-clic en el handle.

## Carga de tablas Excel/CSV (v14)
- Fuente: carpeta con `*.csv` (UTF-8 o UTF-8-BOM, `,` o `;` auto-detectado vía `csv.Sniffer`),
  `*.xlsx` (`openpyxl` `read_only` + `data_only`) y `*.xls` (`xlrd` 2.0.1). Solo 1ª hoja.
  `core/session_loader.load_tablas_folder` (alias `load_csv_folder`) case-insensitive,
  `load_file` dispatch por extensión, cabeceras vacías→`colN`, duplicadas→`_2`, inferencia
  `INTEGER`/`REAL`/`TEXT`. Botón HUD `CSV`→`TABLAS` con tooltip formato completo; `run.spec`
  `hiddenimports=['openpyxl','xlrd']`; `requirements-dev.txt` añade `openpyxl`/`xlrd`/`xlwt`
  (xlwt solo para generar fixtures `.xls` en tests).

## Formato JSON dual (v2, vigente)
`session_loader._normalize_ia_format()` acepta el formato IA del diálogo
(`title/difficulty/statement/expected_hint/defaultQuery/tables[{name,schema{},data[]}]`) y lo
convierte al interno (`ejercicio{titulo,enunciado,pista,dificultad,default_query}/tablas`).
Tipos con sufijo (`INTEGER PRIMARY KEY`) conservan la definición completa; la base se valida contra
`INTEGER, REAL, TEXT, NUMERIC, DATE, BOOLEAN`. Claves extra (`icon`) se ignoran.
