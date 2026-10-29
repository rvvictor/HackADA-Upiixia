# Ficha: contaminación por colonia (real, método por confirmar)

- **Archivo:** `data/raw/colonias_prioritarias.csv` (1,812 filas en el CSV). Sitio, año y método: por confirmar con quien lo descargó. `nivel_contaminacion` (bajo/medio/alto) es, según esa persona, qué tan contaminada está la zona como promedio; no se asume más que eso.
- **Salida:** `data/processed/contaminacion_colonia.json` (sin polígono: se usa el campo `Geo Point` como lat/lng).
- **Columnas de origen:** nueva_clave_colonia, Geo Point, Geo Shape, ENTIDAD, CVE_ALC, Alcaldia, clave_colonia, nombre_colonia, SECC_COM, SECC_PAR, nivel_contaminacion. Salida: `alcaldia_cvegeo`, `colonia`, `clave_colonia`, `nivel_contaminacion`, `lat`, `lng`, `colonia_id`.
- **Distribución (de la nota de origen, 1,811 filas):** medio 662, alto 612, bajo 538.
- **Cruce con el catálogo:** 644 de 1,812 filas cruzan por alcaldía + nombre; 649 colonias del catálogo reciben nivel (más de una fila puede coincidir con la misma colonia). El resto queda `null`.
- **Cobertura:** es un archivo de "colonias prioritarias", no necesariamente de todas las colonias: no interpretar un `null` como "sin contaminación".
- **Sigue simulado:** población, negocios por hexágono, dinero CNBV.
