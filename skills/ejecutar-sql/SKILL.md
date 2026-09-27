---
name: ejecutar-sql
description: Flujo para ejecutar consultas SQL offline con errores en español
---

## Cuándo usar
Al ejecutar una consulta desde el editor (F5 / Ctrl+Enter) o al tocar core/pg_engine.py o core/error_friendly.py.

## Pasos
1. Tomar el texto del editor (`QPlainTextEdit.toPlainText().strip()`).
2. Si vacío, mostrar "Escribe una consulta antes de ejecutar."
3. Llamar a `PGEngine.execute(query)` (PostgreSQL embebido local).
4. Si `ok=False`, mostrar `error` traducido por `friendly_pg_error()` (español principiante).
5. Si `ok=True`, poblar `QTableWidget` con `columns`/`rows` y mensaje "X fila(s)".
6. Guardar en historial (máx. 20) y permitir copiar al portapapeles.
7. Mantener 100% offline: no usar CDN, fetch ni servicios externos.
