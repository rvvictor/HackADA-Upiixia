# Ficha: colonias (real)

- **Archivos:** `data/raw/diccionario_colonias.json` (GeoJSON CRS84, 1,543 colonias, 33.7 MB) y `data/raw/catalogo_colonias/poligonos_colonias_cdmx.*` (shapefile del mismo universo, no usado: el GeoJSON basta). Sitio exacto: por confirmar.
- **Salida:** `data/processed/colonias.json` (1,543 filas, ~0.6 MB). **Sin polígonos:** guardan solo nombre, alcaldía y centroide (lat/lng, centroide del anillo exterior más grande) porque el polígono pesa ~33 MB y el mapa de esta fase no lo necesita.
- **Campos:** `id` (`cve_col`), `colonia`, `alcaldia_cvegeo`, `alcaldia`, `clasif`, `lat`, `lng`, `prioridad`, `marginacion_gm`, `marginacion_im`, `nivel_contaminacion`, `tipo_dato: "real"`, `fuente`, `fecha_consulta: "2026-10-25"`.
- **prioridad:** `true` solo en Coyoacán (09003, 98 colonias) e Iztapalapa (09007, 198): 296 en total.
- **Cruces** (por clave de alcaldía + nombre sin acentos/puntuación): 849 colonias con marginación y 649 con nivel de contaminación; el resto queda en `null` (no se imputa). Los nombres de CONAPO y del catálogo no siempre coinciden, por eso el cruce es parcial.
- **Sigue simulado:** población y negocios por hexágono, dinero CNBV.
