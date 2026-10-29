# Ficha: marginación por colonia (real)

- **Archivo:** `data/raw/indice_marginacion/marginacion.json` (GeoJSON, CONAPO 2020; 2,243 colonias). Sitio exacto de descarga: por confirmar.
- **Salida:** `data/processed/marginacion_colonia.json` (2,243 filas, sin polígono: centroide lat/lng).
- **Columnas de origen usadas:** COLONIA, CP, CVE_MUN, NOM_MUN, IM_2020 (índice), GM_2020 (grado: Muy bajo...Muy alto), IMN_2020 (índice normalizado). Salida: `colonia`, `cp`, `alcaldia_cvegeo`, `im_2020`, `gm_2020`, `imn_2020`, `colonia_id`.
- **Cruce con el catálogo de colonias:** 1,008 de 2,243 filas cruzan (`colonia_id` con la clave del catálogo); 1,235 quedan con `colonia_id: null`. Las 849 colonias del catálogo con marginación aparecen en `colonias.json`. Nada se inventa ni se aproxima por cercanía.
- **Calidad:** el universo de CONAPO (2,243) no coincide con el del catálogo (1,543); hay nombres repetidos por alcaldía y grafías distintas.
- **Todo lo derivado** de estos índices (p. ej. combinarlos con otras capas) va como `estimado`. Sigue simulado: población y dinero CNBV.
