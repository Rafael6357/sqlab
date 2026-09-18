# SPEC: normalizar-nulos-csv-excel

## Meta
- **Feature**: normalizar-nulos-csv-excel
- **Autor**: opencode (Muse Spark)
- **Fecha**: 2026-09-18
- **Estado**: `APPROVED`

## Objetivo
Los CSV/Excel médicos traen celdas "vacías" con espacios (`" "`) o marcadores
(`"-"`, `"NA"`, `"NULL"`, `"null"`, `"NaN"`) que se veían vacías en la grilla.
Normalizarlos a `None` al cargar (paridad con `pandas.read_csv(na_values=[...])`)
para que se muestren como `NULL` (spec `mostrar-null-en-grillas`).

## Acceptance Criteria

### NN-01 — marcadores de nulidad
- **Given** celda CSV/Excel con `" "`, `"-"`, `"NA"`, `"NULL"`, `"null"` o `"NaN"` (con o sin espacios alrededor)
- **When** cargar
- **Then** la celda es `None` (grilla pinta `NULL` tenue, export escribe `NULL`).

### NN-02 — datos reales intactos
- **Given** celdas `" x "`, `"N/A"`, `0`, números, fechas
- **When** cargar
- **Then** se conservan tal cual (`"N/A"` no está en el set, igual que el `na_values` explícito del usuario).

### NN-03 — filas cortas
- **Given** fila CSV con menos campos que columnas
- **When** cargar
- **Then** el relleno es `None` (antes `""`).

### NN-04 — JSON intacto
- **Given** JSON con strings `"NA"` explícitos
- **When** cargar
- **Then** se respetan (el JSON tiene `null` real; no se aplica el set).

## Edge Cases
- [x] Celda con solo espacios múltiples `"   "` → `None`.
- [x] `"NA"` legítimo (iniciales, Namibia) → `None` (limitación conocida, igual que pandas con `keep_default_na`).
- [x] Excel numérico/fecha/bool intactos (el helper solo mira strings y `None`).
- [x] Inferencia de tipos: los marcadores no contaminan la muestra (ya se saltan vacíos; `"NA"`/`"-"` infieren TEXT, correcto).

## Límites Conocidos
- `"",` vs `"","",` indistinguibles en CSV: ambos → `None` (coherente con el loader JSON).
- Set exacto del usuario: `{"", "-", "NA", "NULL", "null", "NaN"}` (+ strip). No se aplica el resto del `keep_default_na` de pandas (`"#N/A"`, etc.).

## Archivos a tocar
- `core/session_loader.py` (helper `_es_nulo` + `_parse_csv` + `_parse_excel`)
- `tests/test_normalizar_nulos.py` (nuevo: NN-01..NN-04)

## Tests requeridos
- **Unit**: CSV con cada marcador → `None`; `" x "`/`"N/A"`/números intactos; fila corta → `None`; xlsx con marcadores → `None`.
- **E2E**: CSV cargado → visor pinta `NULL`.
- **Nombre de archivos de test**: `tests/test_normalizar_nulos.py`

## Notas de diseño
- Causa raíz del reporte con foto: el CSV ya convertía `""`→`None`, pero las celdas con `" "` se conservaban y se veían vacías pese al render NULL de v21.
- Helper compartido para CSV y Excel; JSON excluido a propósito.
