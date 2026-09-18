# Contribuir

## Antes de un PR
- `ruff check .`
- `python -m py_compile app.py core/*.py ui/*.py`

## Commits
`tipo(alcance): mensaje corto`
Ej: `fix(sql): traduce error de sintaxis cerca de "FORM"`

## Checklist
- [ ] La app abre sin internet (sin CDN: sin Tailwind/Google Fonts/FontAwesome)
- [ ] Solo modo oscuro cyber fósforo (no se agregó variante clara)
- [ ] Pista sigue colapsada por defecto
- [ ] Autocompletado sigue OFF por defecto (checkbox AUTOCOMPLETAR)
- [ ] Se probó carga `.json` clásico y formato IA (`title/tables/schema/data` + `defaultQuery`)
- [ ] Se probó CARGAR TABLAS (archivos múltiples + carpeta, `.csv`/`.xlsx`/`.xls`) y presets Tienda/Biblioteca
- [ ] EJECUTAR muestra badge `N FILAS` + tiempo; el error se muestra en español
- [ ] COPIAR PARA IA y PLANTILLA JSON PARA IA copian al portapapeles
- [ ] Los nulos se ven como `NULL` tenue (no vacíos); EXPORTAR CSV escribe `NULL`
