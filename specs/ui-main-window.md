# SPEC: Ventana principal SQLab (UI completa)

- **Feature**: UI principal de la aplicación SQLab — HUD, consola, matrix, dialogs, historial, sesiones
- **Estado**: IMPLEMENTADO (v1-v9, diseño final v8 SQLab)
- **Archivo**: `ui/main_window.py` (~1126 líneas)
- **Tests**: `tests/test_e2e_smoke.py` (26 tests E2E con Qt offscreen)

## Objetivo
Proveer la interfaz gráfica completa de SQLab: carga de ejercicios (JSON/CSV), ejecución SQL en vivo, historial, pista/aula, formateo, portapapeles, guardar/cargar sesión, y diálogos informativos — todo en modo oscuro cyberpunk 100% en español.

## Layout de la UI (referencia: design.md Líneas 26-57)
```
┌─────────────────────────────────────────────────────────┐
│  HUD: [logo 26px] SQLab │ btns: FORMATO JSON IA, CARGAR, CSV/SAV/SES │
├─────────────────────────────────────────────────────────┤
│  BANNER: [NIVEL]: PRINCIPIANTE ★☆☆ │ [MISIÓN]: título  │
│  VER_PISTA/OCULTAR_PISTA │ EJEMPLO: TIENDA/BIBLIOTECA  │
├──────────────┬──────────────────────────────────────────┤
│  MATRIZ      │  WORKSPACE                               │
│  (288px)     │  ┌ TAB: [DIRECTIVA] [VOLCADO] ─────────┐│
│  nodos tabla │  │ EJERCICIO: enunciado + columnas       ││
│  columnas    │  └──────────────────────────────────────┘│
│  SELECT *    │  ┌ CONSOLE ─────────────────────────────┐│
│  HISTORIAL   │  │ FORMATO │ AC │ COPIAR PARA IA         ││
│              │  │ EJECUTAR_SQL │ EDITOR SQL              ││
│              │  └──────────────────────────────────────┘│
│              │  ┌ RESULTADO ────────────────────────────┐│
│              │  │ MATRIZ DE RESULTADOS (tabla QTable)    ││
│              │  │ Badge: FILAS │ T_EJEC │ ESTADO         ││
│              │  └──────────────────────────────────────┘│
└──────────────┴──────────────────────────────────────────┘
```

## Acceptance Criteria

### Boot / Inicialización

#### SC-01: La app inicia correctamente
- **Given** se ejecuta `MainWindow()` sin datos previos
- **When** se crea la ventana
- **Then** `windowTitle()` contiene `"SQLab"`, `engine.connected = True`, hay al menos 1 tabla cargada

#### SC-02: Preset inicial se carga automáticamente
- **Given** la app arranca sin sesión previa
- **When** `MainWindow()` termina de inicializar
- **Then** `tabla_list.count() >= 2` (ejemplo_tienda), `tables_count.text() = "(2)"`, `exercise_title` no contiene `"SIN EJERCICIO"`

#### SC-03: Editor tiene default_query del preset
- **Given** se carga el preset inicial (ejemplo_tienda)
- **When** se inspecciona el editor
- **Then** `editor.toPlainText()` contiene `"SELECT"` y al menos uno de `"clientes"` o `"pedidos"`

### Ejecución SQL

#### SC-04: SELECT * muestra todos los registros
- **Given** tabla `clientes` con 4 filas y 3 columnas
- **When** se ejecuta `SELECT * FROM clientes;`
- **Then** `resultado_tabla.isVisible() = True`, `resultado_tabla.rowCount() = 4`, `resultado_tabla.columnCount() = 3`, `row_badge.text()` contiene `"FILAS"`

#### SC-05: WHERE filtra correctamente
- **Given** tabla `clientes` con 4 filas
- **When** se ejecuta `SELECT nombre FROM clientes WHERE id = 1;`
- **Then** `resultado_tabla.rowCount() = 1`, celda (0,0) contiene `"Ana Pérez"`

#### SC-06: Error de sintaxis muestra error_box
- **Given** una consulta con error (`SELEC * FROM clientes;`)
- **When** se ejecuta
- **Then** `error_box.isVisible() = True`, `resultado_tabla.isVisible() = False`, `error_text.text()` no está vacío

#### SC-07: Editor vacío produce error
- **Given** el editor está vacío
- **When** se ejecuta
- **Then** `error_box.isVisible() = True`, `error_text.text()` contiene `"VACÍO"` o `"vacía"`

#### SC-08: Consulta exitosa se añade al historial
- **Given** el historial tiene N elementos
- **When** se ejecuta `SELECT COUNT(*) FROM clientes;` exitosamente
- **Then** `len(historial) = N + 1`, `historial_list.count() >= N + 1`

### FORMATO toggle

#### SC-09: FORMATO es checkable y formatea SQL
- **Given** `btn_format.isCheckable() = True` y `btn_format.isChecked() = False`
- **When** se llama `formatear_consulta()` con `"select * from clientes"` en el editor
- **Then** `btn_format.isChecked() = True`, el editor contiene `"SELECT"`, `"FROM"`, `"clientes"`

### Modal Formato JSON

#### SC-10: Diálogo contiene CLAUDE_PROMPT
- **Given** la función `mostrar_formato_json` está disponible
- **When** se llama (sin bloquear el evento loop, monkeypatch `QDialog.exec`)
- **Then** un `QPlainTextEdit` con contenido `CLAUDE_PROMPT` (módulo constante, ≥100 chars) es visible

#### SC-11: Botón COPIAR PLANTILLA copia al portapapeles
- **Given** el diálogo JSON está abierto
- **When** se hace click en el botón `COPIAR PLANTILLA`
- **Then** `QGuiApplication.clipboard().text() == CLAUDE_PROMPT`

### COPIAR PARA IA

#### SC-12: copiar_consulta pone el contenido en el portapapeles
- **Given** el editor contiene `"SELECT nombre FROM clientes;"`
- **When** se llama `copiar_consulta()`
- **Then** `QGuiApplication.clipboard().text()` contiene `"SELECT nombre FROM clientes"`

### VER SELECT *

#### SC-13: ver_select_all inyecta y ejecuta SELECT *
- **Given** la tabla `clientes` está seleccionada en `tabla_list`
- **When** se llama `ver_select_all()`
- **Then** el editor contiene `"SELECT * FROM"`, `resultado_tabla.isVisible() = True`, `resultado_tabla.rowCount() > 0`

### Limpiar

#### SC-14: limpiar_editor vacía el editor
- **Given** el editor contiene `"SELECT 1;"`
- **When** se llama `limpiar_editor()`
- **Then** `editor.toPlainText() == ""`

#### SC-15: limpiar_historial vacía el historial
- **Given** hay al menos 1 elemento en el historial
- **When** se llama `limpiar_historial()`
- **Then** `historial == []`, `historial_list.count() == 0`

### Pista toggle

#### SC-16: Pista se muestra al activar toggle
- **Given** `pista_toggle.isChecked() = False` y `pista_card.isVisible() = False`
- **When** se hace click en `pista_toggle` (checked = True)
- **Then** `pista_card.isVisible() = True`, `pista_toggle.text() == "OCULTAR_PISTA"`

#### SC-17: Pista se oculta al desactivar toggle
- **Given** la pista está visible (`pista_card.isVisible() = True`)
- **When** se hace click en `pista_toggle` (checked = False)
- **Then** `pista_card.isVisible() = False`, `pista_toggle.text() == "VER_PISTA"`

### Matrix list

#### SC-18: Seleccionar tabla muestra sus columnas
- **Given** la tabla `clientes` está seleccionada en `tabla_list`
- **When** se inspecciona `columnas_list`
- **Then** `columnas_list.count() > 0` (las columnas de la tabla se muestran)

### Guardar / Cargar sesión

#### SC-19: Guardar sesión crea JSON válido con tablas e historial
- **Given** hay tablas cargadas e historial con al menos 1 consulta
- **When** se llama `guardar_sesion()` (con `QFileDialog.getSaveFileName` mockeado)
- **Then** se crea un archivo JSON con claves `"tablas"` (len >= 2) e `"historial"` (len >= 1)

#### SC-20: Cargar sesión restaura tablas e historial
- **Given** un archivo de sesión guardado previamente
- **When** se llama `cargar_sesion()` (con `QFileDialog.getOpenFileName` mockeado)
- **Then** `engine.table_names()` incluye `"clientes"`, `len(historial)` == el valor guardado

#### SC-21: Guardar sin tablas muestra error
- **Given** el engine no tiene tablas cargadas
- **When** se llama `guardar_sesion()`
- **Then** se muestra un diálogo de error (via `_show_custom_dialog`)

### Carga directa de archivos

#### SC-22: Cargar JSON interno reemplaza tablas
- **Given** tablas actuales son `["clientes", "pedidos"]`
- **When** se carga `ejemplo_biblioteca.json`
- **Then** `engine.table_names()` incluye `"libros"`, `"usuarios"`, `"prestamos"`, `tabla_list.count() == 3`

#### SC-23: Carga de carpeta CSV crea tablas
- **Given** una carpeta con 2 archivos CSV (clientes, productos)
- **When** se aplica el resultado via `_aplicar_resultado`
- **Then** `engine.table_names()` incluye `"clientes"` y `"productos"`

### Autocompletado

#### SC-24: Autocompletado está desactivado por defecto
- **Given** la app arranca sin configuración previa
- **When** se inspecciona `autocomplete_check`
- **Then** `autocomplete_check.isChecked() == False`

### Close event

#### SC-25: Cerrar ventana cierra la conexión del motor
- **Given** la app está abierta con `engine.connected = True`
- **When** se llama `closeEvent()`
- **Then** `engine.connected == False`

### Toast

#### SC-26: _toast actualiza barra de estado
- **Given** la función `_toast` está disponible
- **When** se llama `_toast("TEST MESSAGE")`
- **Then** `exec_time.text() == "TEST MESSAGE"`, `mensaje_label.text() == "TEST MESSAGE"`

### Briefing

#### SC-27: Briefing se actualiza al cargar preset
- **Given** se carga un preset con título y dificultad
- **When** `_refresh_briefing()` se ejecuta
- **Then** `difficulty_badge.text()` contiene la dificultad, `exercise_title.text()` no es `"SIN EJERCICIO"`

## Edge Cases
- Ejecutar sin tablas: error descriptivo (SC-07 cubre editor vacío; sin tablas cubierto en sqlite-engine SC-07)
- Guardar sesión con historial vacío: funciona (historial: [])
- Cargar sesión corrupta: error de JSON parse
- Formatear editor vacío: no crash, `formatear_consulta` retorna sin cambios
- Limpiar editor vacío: no crash
- Cerrar con diálogo modal abierto: Qt maneja al cerrar ventana padre

## Archivos a tocar
- `ui/main_window.py` (NO TOCAR — módulo base estable)
- `resources/dark.qss` (NO TOCAR — solo modo oscuro)

## Notas de diseño
- `_show_custom_dialog` reemplaza QMessageBox para diálogos informativos (warning, error, info)
- `CLAUDE_PROMPT` es una constante de módulo (string, ~687 chars) que define la plantilla para IA
- `btn_format.setCheckable(True)` con `formatear_consulta()` forzando checked
- Historial almacena solo strings de consulta; max ~20 elementos (se descartan los más antiguos)
- `QDialog.exec` monkeypatcheado en tests para no bloquear el event loop
- `QFileDialog.getSaveFileName/getOpenFileName` monkeypatcheados para tests offscreen
