---
name: cargar-sesion
description: Flujo para cargar y validar archivos de ejercicio (JSON/CSV) en SQLPractica
---

## Cuándo usar
Cuando el usuario carga un ejercicio nuevo (botones Cargar ejercicio / Cargar tablas) o al implementar cambios en core/session_loader.py.

## Pasos
1. Detectar formato por extensión: `.json` → parse JSON, `.csv` → inferencia de tipos.
2. Validar nombres de tabla/columna (solo letras, números, guiones bajos).
3. Validar tipos contra `INTEGER, REAL, TEXT, NUMERIC, DATE, BOOLEAN`; fallback a TEXT.
4. Si hay errores, devolver `LoadResult(ok=False, errors=[...])` con mensajes en español.
5. Si ok, inyectar en `SQLEngine.load_tables()` y refrescar lista de tablas + enunciado.
6. CSV en carpeta: usar `load_csv_folder()` (un archivo = una tabla).
