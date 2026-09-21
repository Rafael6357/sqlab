# SQLab — Laboratorio offline para practicar SQL

Consola estilo TUI con directiva de misión, matriz de esquema, consola SQL con atajo y matriz de resultados con diagnósticos. Local y en español para practicar SQL con IAs como Claude. Sin internet, sin modo claro, solo fósforo verde.

## Stack

- Python 3.11 + **PySide6** (Qt) + **sqlite3** (stdlib, en memoria)
- Build: PyInstaller → `.exe` portable (Windows)

Justificación: `sqlite3` ya viene en Python, Qt es 100% offline (sin CDN), un solo `.exe` sin instalar nada. Se descartaron Electron/Tauri (pesados) y C# WPF (requiere .NET SDK).

## Levantar en local

```powershell
pip install -r requirements.txt
python app.py
```

Generar `.exe` portable:

```powershell
pip install pyinstaller
.\bin\build.ps1        # usa run.spec (onefile, windowed, incluye recursos)
# El .exe queda en dist/SQLab.exe
```

Equivalente manual desde la raíz del repo:

```powershell
pyinstaller --noconfirm --clean run.spec
```

## Formato de archivo de ejercicio

### Principal: `.json` (un archivo = un ejercicio)

Fácil de generar por IA y de validar.

```json
{
  "ejercicio": {
    "titulo": "Práctica 01 — Tienda",
    "enunciado": "Muestra nombre y precio de productos con precio > 100...",
    "pista": "Usa WHERE y ORDER BY"
  },
  "tablas": [
    {
      "nombre": "productos",
      "columnas": [
        {"nombre": "id", "tipo": "INTEGER"},
        {"nombre": "nombre", "tipo": "TEXT"},
        {"nombre": "precio", "tipo": "REAL"}
      ],
      "filas": [[1, "Laptop", 1200.5], [2, "Mouse", 25.0]]
    }
  ]
}
```

Tipos válidos: `INTEGER, REAL, TEXT, NUMERIC, DATE, BOOLEAN` (se acepta sufijo como `INTEGER PRIMARY KEY`). Si el JSON no se puede interpretar se muestra un error con el motivo.

### Alternativo: formato IA (generado por IA)

El botón **JSON IA** muestra el prompt para pedir quests a IA. Ese formato también carga directamente (acepta `defaultQuery`/`default_query` e ignora claves extra como `icon`):

```json
{
  "title": "Top Clientes por Gasto Total en 2023",
  "difficulty": "Principiante ★☆☆",
  "statement": "Devuelve el nombre del cliente y el total gastado en 2023...",
  "expected_hint": "Usa INNER JOIN, LIKE '2023%' y SUM(monto)...",
  "defaultQuery": "SELECT c.nombre, SUM(p.monto) AS total_gastado FROM clientes c ...",
  "tables": [
    {
      "name": "clientes",
      "schema": {"id": "INTEGER PRIMARY KEY", "nombre": "TEXT", "ciudad": "TEXT"},
      "data": [[1, "Ana Pérez", "Madrid"], [2, "Carlos Gómez", "Barcelona"]]
    }
  ]
}
```

`title→titulo`, `statement→enunciado`, `expected_hint→pista`, `difficulty→dificultad` (badge `Misión X`).

Prompt para IA: *"Genera el ejercicio en el formato JSON anterior con 2–3 tablas y menos de 50 filas por tabla"*. Ejemplos incluidos: `ejemplo_tienda.json` y `ejemplo_biblioteca.json`.

### Secundario: `.csv` (una carpeta = varias tablas)

Selecciona una carpeta con archivos `.csv`. Cada archivo → una tabla. El nombre del archivo es el nombre de la tabla (`clientes.csv` → tabla `clientes`). Primera fila = cabecera. Tipos inferidos automáticamente.

Ejemplo en `examples/csv/`.

## Uso de la app (SQLab, todo en español)

1. Cargar base con **CARGAR**: **EJERCICIO (.json)** (formato clásico o IA), **TABLAS** desde archivos (`*.csv`/`*.xlsx`/`*.xls`/`.db`, multi-selección) o carpeta, o **EJEMPLO: TIENDA / BIBLIOTECA**.
2. Explora el **ESQUEMA DE TABLAS** (clic en una tabla la vuelve **TABLA ACTIVA:** y muestra su **CONTENIDO DE LA TABLA**; anchos auto-ajustados al contenido con reparto proporcional).
3. Lee el **[EJERCICIO]** (enunciado + columnas objetivo + botón **COPIAR**). La **PISTA:** está colapsada por defecto.
4. Escribe la consulta en el editor vacío (resaltado fósforo, `AUTOCOMPLETAR` OFF por defecto: Enter/Tab acepta, funciones con `()` y `(` se autocierra). Botón **FORMATO SQL** con indentación real. Dialecto SQLite con ayudas PostgreSQL (`::`→`CAST`, hints de `date_part`/`USING`/etc.).
5. **EJECUTAR_SQL (Ctrl+Enter / F5)**: el **RESULTADO DE LA CONSULTA** muestra badge `N FILAS` y tiempo; los nulos se ven como `NULL` tenue (no confundir con vacío); si falla, error en español vía `HISTORIAL DE CONSULTAS` (contraído por defecto, toggle `VER_HISTORIAL`).
6. **COPIAR PARA IA** exporta misión + consulta con plantilla; **EXPORTAR CSV / EXPORTAR EXCEL** guardan el resultado completo (`NULL` incluido).
7. **GUARDAR SESIÓN / CARGAR SESIÓN** conserva tablas + historial. Barra de estado: `TABLAS: N · FILAS: M · DB: MEMORIA OK`. Cronómetro por ejercicio en el HUD.

## Variables de entorno

No requiere. Todo es local y en memoria (`:memory:`).

## Estructura

```
app.py
requirements.txt / requirements-dev.txt
pyproject.toml          # pytest + ruff (`ruff check .`)
core/
  sqlite_engine.py    # BD en memoria, execute() multi-sentencia + :: → CAST
  session_loader.py   # valida JSON/CSV/XLSX/XLS/DB + nulos estilo pandas
  error_friendly.py   # errores en español + hints PostgreSQL
ui/
  main_window.py      # ventana principal (~1100 lín., mixins)
  crono.py            # CronoMixin (cronómetro/temporizador)
  paneles.py          # PanelesMixin (HUD/banner/pista/matriz)
  formato_sql.py      # formateador SQL real (tokenizador)
  dialogs.py          # diálogos custom + plantilla para IA
  tablas.py           # grillas: anchos, NULL tenue, reparto proporcional
  sql_highlighter.py  # resaltado SQL fósforo
resources/
  dark.qss            # tema oscuro único (scrollbars visibles 12px)
  logo_sqllab.svg/.ico# logo SQLab (ventana + HUD + exe)
examples/
  ejemplo_tienda.json       # quest Top Clientes 2023
  ejemplo_biblioteca.json   # quest Libros con retraso
  csv/                      # clientes.csv, productos.csv
tests/ (286) · specs/ (34, ver specs/INDEX.md)
```
