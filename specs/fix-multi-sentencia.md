# Spec: fix-multi-sentencia

> Estado: APPROVED — bugfix SDD (el formateador genera multi-sentencia
> `SELECT 1;\nSELECT 2;` pero `execute()` solo acepta una: `ProgrammingError`
> "You can only execute one statement at a time").

## Objetivo
El editor acepta scripts con varias sentencias `;`: se ejecutan en orden y
se muestra el último resultado con filas. Sin crash, con error amable si
alguna falla. El `;` dentro de literales o comentarios no parte.

## Acceptance criteria (Given/When/Then)
- **MS-01**: Given `SELECT 1; SELECT 2;`, When ejecutar, Then filas `[[2]]`.
- **MS-02**: Given script `CREATE TABLE m (a); INSERT INTO m VALUES (7); SELECT * FROM m;`,
  When ejecutar, Then filas `[[7]]` (DDL + DML + SELECT encadenados).
- **MS-03**: Given `SELECT 1; SELEKT 2;`, When ejecutar, Then error amable
  (sin excepción fuera de `execute`).
- **MS-04**: Given `SELECT 'a;b'; SELECT 2;`, When ejecutar, Then `[[2]]`
  (el `;` del literal no parte).
- **MS-05**: Given una sola sentencia, When ejecutar, Then comportamiento
  intacto.

## Edge cases
- `;;;` o vacío → mensaje "Escribe una consulta…" (como hoy).
- Última sentencia sin filas (DDL) → mensaje `N sentencias ejecutadas`.
- Comentarios `-- ;` y `/* ; */` no parten.

## Límites conocidos
- Sin transacciones explícitas entre sentencias (cada una hace commit como hoy).
- Se muestra solo el ÚLTIMO resultado con filas (estándar de consolas simples).

## Requisitos de testing
- `tests/test_multi_sentencia.py`: MS-01..MS-05 (unit engine + 1 E2E).
- `python -m pytest -q` 100 % + build.
