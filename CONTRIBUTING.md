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
- [ ] Autocompletado sigue OFF por defecto (checkbox AC)
- [ ] Se probó carga `.json` clásico y formato IA (`title/tables/schema/data` + `defaultQuery`)
- [ ] Se probó carga `.csv` y presets Tienda/Biblioteca
- [ ] EXECUTE muestra badge ROWS + EXEC_TIME; error muestra 0x22 + recovery advice
- [ ] COPY FOR IA y modal JSON copian al portapapeles
- [ ] Errores de SQL se muestran en español
