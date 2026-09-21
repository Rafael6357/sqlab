# SPEC: abrir-db-existente

## Meta
- **Feature**: abrir-db-existente
- **Autor**: opencode (Muse Spark)
- **Fecha**: 2026-09-18
- **Estado**: `APPROVED`

## Objetivo
Cargar ficheros SQLite existentes (`.db`, `.sqlite`, `.sqlite3`) como sesión
de análisis: cada tabla del fichero → una tabla en memoria (solo lectura del
fichero; la app no lo modifica).

## Acceptance Criteria

### DB-01 — tablas y datos
- **Given** un `.db` con tablas, tipos y nulos
- **When** `load_file`
- **Then** `ok`, una `Table` por tabla de usuario (sin `sqlite_%`), columnas con tipo declarado (fallback `TEXT`) y filas con `None` intactos.

### DB-02 — extensiones y UI
- **Given** el diálogo CARGAR TABLAS
- **When** elegir modo ARCHIVOS o CARPETA
- **Then** el filtro incluye `*.db *.sqlite *.sqlite3` y la carpeta los recoge (case-insensitive); tooltip documenta el formato.

### DB-03 — fichero ajeno no rompe
- **Given** un `.db` inexistente/corrupto o sin tablas
- **When** cargar
- **Then** `LoadResult(ok=False)` con error en español, sin crash y sin tocar la sesión actual.

### DB-04 — solo lectura
- **Given** un `.db`
- **When** cargar
- **Then** el fichero no se modifica (apertura `mode=ro`; ni WAL ni journal laterales).

## Edge Cases
- [x] Tablas vacías (0 filas): se cargan con sus columnas.
- [x] Nombres con espacios/unicode: el engine ya entrecomilla.
- [x] Tipos raros (`VARCHAR(255)`, `BLOB`): se conserva el declarado (SQLite es flexible); bytes pasan como `bytes`.
- [x] `.db` grande: aplica el aviso >50 MB existente (`_confirmar_archivo_grande` incluye `.db`).

## Límites Conocidos
- Se vuelcan tablas completas a memoria (igual que CSV/Excel hoy); sin paginación.
- Sin escritura al fichero: el análisis (DDL) vive solo en memoria (exportar `.db` es Fase B1).
- Los textos `"NA"`/`"-"` de un `.db` se respetan (dato explícito, como JSON).

## Archivos a tocar
- `core/session_loader.py` (`_parse_db` + dispatch en `load_file`)
- `ui/main_window.py` (filtros ARCHIVOS/CARPETA, aviso de tamaño, tooltip)
- `tests/test_abrir_db.py` (nuevo: DB-01..DB-04)

## Tests requeridos
- **Unit**: `.db` real (sqlite3) con 2 tablas + nulos + tabla vacía; corrupto; sin tablas; `.sqlite3`.
- **E2E**: `SELECT` sobre tabla cargada desde `.db` vía engine.
- **Nombre de archivos de test**: `tests/test_abrir_db.py`

## Notas de diseño
- Conexión `mode=ro` por URI: garantiza no-modificación incluso ante bugs.
- `sqlite_master` excluyendo `sqlite_%`; esquema vía `PRAGMA table_info`.
