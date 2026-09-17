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

1. Cargar ejercicio: **CARGAR EJERCICIO (.json)** (formato clásico o IA), **CSV**, o **EJEMPLO: TIENDA / BIBLIOTECA**.
2. Explora la **MATRIZ DE ESQUEMA** (nodos `> tabla [NF]`; clic en `# columna` la inyecta; `INSERTAR SELECT *`; `REGISTRO DE TRANSACCIONES` con `[LIMPIAR]`, clic recarga+ejecuta).
3. Lee **[DIRECTIVA DE MISIÓN]** (especificación + objetivo, COLUMNAS OBJETIVO, ORDEN). La pista está colapsada (`VER_PISTA` → `[IA_DESCIFRADO]`).
4. Escribe la consulta en la **CONSOLA** (resaltado fósforo, `LÍN/COL`, `DIALECTO: SQLITE3`). Autocompletado OFF por defecto (checkbox `AC`). Botón **FORMATO** (toggle que queda marcado al activarse).
5. **EJECUTAR_SQL (Ctrl+Enter / F5)**: badge `N FILAS`, `T_EJEC: ms // ESTADO: 200 OK`, o `EXCEPCIÓN_SINTAXIS_SQLITE CÓD_ERROR: 0x22` + `CONSEJO DE RECUPERACIÓN` en español si falla.
6. **COPIAR PARA IA** exporta misión + query con plantilla lista para pegar en IA.
7. El modal **FORMATO JSON IA** (`COPIAR PLANTILLA`, muestra toast de confirmación) genera el prompt para pedir nuevos retos a IA. Guardar/Cargar sesión (`SAV`/`SES`, incluye tablas + historial).

## Variables de entorno

No requiere. Todo es local y en memoria (`:memory:`).

## Estructura

```
app.py
requirements.txt
core/
  sqlite_engine.py    # BD en memoria, execute()
  session_loader.py   # valida JSON/CSV/XLSX/XLS
  error_friendly.py   # errores en español
ui/
  main_window.py      # Ventana principal SQLab (HUD/mission/matrix/consola/matriz)
  sql_highlighter.py  # resaltado SQL fósforo
resources/
  dark.qss            # tema oscuro único (paleta cyber phosphor)
  logo_sqllab.svg     # logo SQLab (ícono de ventana + chip HUD)
examples/
  ejemplo_tienda.json       # quest Top Clientes 2023
  ejemplo_biblioteca.json   # quest Libros con retraso
  csv/
```
