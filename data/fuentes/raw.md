# Fuente: archivos oficiales en `data/raw/` (no se versionan; `data/raw/` está en `.gitignore`)

Consultados el domingo 2026-10-25 en datos.cdmx.gob.mx, INEGI, CONAPO y SIEG CDMX. Copiados a `data/raw/` el 2026-10-29.
Qué archivo viene de qué sitio: por confirmar con quien los descargó (Victor) antes de citarlo en la UI.

| Archivo | Contenido | Filas | Notas |
|---|---|---:|---|
| `ubicacion_tianguis.csv` | Tianguis: alcaldía, colonia, ubicación, giro, día, horario, lat/lng | 1,367 | Acentos mal codificados (`BRASILEÃ‘OS`); alcaldía con variantes (`COYOACÁN`/`COYOACAN`). Normalizar al procesar. |
| `diccionario_tianguis.csv` | Mercados públicos: número, locales, dirección, colonia, tipo, superficie m², año, giro, coordenadas | 329 | Coordenadas en columnas `longitud,latitud` (en ese orden). |
| `diccionario_colonias.json` | Polígonos GeoJSON de colonias (CRS84) | 1,543 | Propiedades: `cve_alc`, `alc`, `cve_col`, `colonia`, `clasif`. |
| `catalogo_colonias/poligonos_colonias_cdmx.*` | Catálogo de colonias en shapefile (WGS84) | - | Mismo universo de colonias, otro formato (2023). |
| `colonias_prioritarias.csv` | Colonias con polígono, alcaldía y `nivel_contaminacion` (bajo/medio/alto) | 1,811 | `nivel_contaminacion` = qué tan contaminada está la zona, como promedio (según quien lo descargó; año y método por confirmar). |
| `indice_marginacion/marginacion.json` | Índice de marginación por colonia (CONAPO): `IM_2020`, `GM_2020`, `IMN_2020`, CP, alcaldía | 2,243 | Año 2020. |

Todo lo que salga de estos archivos lleva `tipo_dato: "real"` con el nombre del archivo y la fecha de consulta (2026-10-25). Lo calculado sobre ellos va como `estimado`.
Sigue simulado: población por hexágono, negocios por hexágono (hasta conectar DENUE) y dinero CNBV.
