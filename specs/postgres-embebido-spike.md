# SPEC: postgres-embebido-spike (F0, gate go/no-go)

## Meta
- **Feature**: postgres-embebido-spike
- **Autor**: opencode (Muse Spark)
- **Fecha**: 2026-09-21
- **Estado**: `APPROVED`

## Objetivo
Probar ANTES de migrar que PostgreSQL embebido es viable: instalar vía pip,
levantar servidor efímero local, conectar con `psycopg`, ejecutar dialecto
PG real (`date_part`, `::`, `USING`, booleanos) y mapear cómo se empaquetaría
(binarios + DLLs para `run.spec`).

## Acceptance Criteria (aprobado manual, no suite)

### SP-01 — instalación
- **Given** intérprete del proyecto
- **When** `pip install pgserver "psycopg[binary]"`
- **Then** instala sin errores.

### SP-02 — servidor efímero + dialecto
- **Given** `pgserver.get_server(pgdata_temporal)`
- **When** conectar y correr `SELECT date_part('year', DATE '2024-05-01')`, `'5'::INTEGER + 1`, `JOIN ... USING(id)`, booleanos y `RETURNING`
- **Then** todo ok con valores esperados.

### SP-03 — layout empaquetable
- **Given** el paquete instalado
- **When** inspeccionar su carpeta de binarios (`initdb`, `postgres`, DLLs)
- **Then** listado de rutas para `datas`/`binaries` de `run.spec` + tamaño estimado.

## Límites Conocidos
- El spike NO toca la app (script temporal fuera del repo-track o en `bin/`).
- La prueba en máquina limpia real queda para F6; aquí solo layout + arranque local.

## Veredicto
- **GO** si SP-01..SP-03 pasan → F1.
- **NO-GO** si el arranque falla o el peso/complejidad es inasumible → se documenta y se queda SQLite + compat.
- **ESTADO 2026-09-21: BLOQUEADO a la espera del zip** — `pgserver` no existe
  en PyPI; `testing.postgresql` exige binarios locales; sin PG local ni admin;
  EDB bloquea descargas automáticas (403). El usuario descarga el zip manual.
- **RESULTADO 2026-09-27: GO** — zip `postgresql-17.11-4` verificado (380 MB,
  21961 archivos); vendoreado `pgsql/{bin,lib,share}` = 134.5 MB.
  `initdb` 9 s, arranque+conexión 0.7 s, `date_part`/`::`/`USING`/`RETURNING`/
  booleanos OK, parada limpia. Hallazgo: `pg_ctl start` se cuelga en este
  entorno (el servidor sí levanta); la app lanzará `postgres.exe` directo
  vía `Popen` + poll TCP + `terminate`.
