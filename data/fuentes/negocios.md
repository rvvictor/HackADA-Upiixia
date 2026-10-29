# Fuente · negocios, diccionario de artículos y programas (PB-005)

| Archivo | Qué es hoy | Tipo | Fuente real que lo reemplaza |
|---|---|---|---|
| `data/processed/negocios.json` | 520 negocios con la forma del DENUE (nombre, razón social, clase SCIAN, estrato, ubicación) en Coyoacán (09003) e Iztapalapa (09007), generados con semilla fija por `uv run python -m pipeline.negocios`. 35% cerca de la sede (San Lucas, Coyoacán) para la demo de la ruta. | **simulado** (`tipo_dato: "simulado"` en cada registro) | DENUE de INEGI: API `BuscarAreaActEstr` o la descarga masiva del DENUE CDMX (términos de libre uso INEGI) |
| `data/processed/articulo_giro.json` | 332 artículos de uso diario en México con sinónimos chilangos, escritos a mano por el equipo (sin LLM), con sus clases SCIAN | construido a mano | Ampliación a ≥ 2,000 artículos (IDEA.md A.5) y eval de 150 artículos |
| `data/processed/programas.json` | Mercomuna, DiMo y CoDi (existen), "Crece tu Mipyme con pagos digitales" (por verificar), Puntos de barrio (propuesta de Pulso Barrial) | real / propuesta, según `estado` | Fuentes oficiales: directorio Mercomuna, Banxico |

## Regla anti-cadenas (real)

`pipeline/negocios/filtros.py` aplica los 4 filtros de IDEA.md A.7 en orden y guarda el motivo en `motivo_exclusion`:

1. **Giro:** supermercados (462111), minisúpers y tiendas de conveniencia (462112), tiendas departamentales (462210).
2. **Tamaño:** solo estratos "0 a 5 personas" y "6 a 10 personas".
3. **Nombre:** lista negra `pipeline/negocios/cadenas.txt`, coincidencia difusa `rapidfuzz.partial_ratio ≥ 90` (las marcas de ≤ 5 letras, como OXXO o KFC, solo como palabra completa).
4. **Repetición:** el mismo nombre o razón social 5 o más veces.

Con los datos simulados excluye 50 de 520: 30 por giro, 12 por nombre, 6 por repetición ("Tacos Don Manolito", que no está en la lista negra) y 2 por tamaño.

## Pendiente para datos reales

- Confirmar las claves SCIAN de `pipeline/negocios/clases.py` en el catálogo SCIAN 2018 de INEGI antes de correr sobre el DENUE.
- Confirmar las URLs exactas de DiMo y CoDi en Banxico (hoy apuntan a la página principal) y los requisitos de afiliación de Mercomuna.
