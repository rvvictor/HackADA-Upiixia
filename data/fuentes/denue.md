# Ficha de fuente · DENUE (INEGI)

**Qué es.** Directorio Estadístico Nacional de Unidades Económicas del INEGI: establecimientos con nombre, giro (clase de actividad), estrato de personal y coordenadas. Alimenta los negocios locales **reales** de colonIA (`tipo: "negocio_local"`, `tipo_dato: "real"`).

**Fuente y cita.** DENUE, INEGI. Cítese como "Fuente: INEGI, DENUE". Términos de uso de INEGI: libre uso con cita de la fuente (https://www.inegi.org.mx/inegi/terminos.html).

**Consulta.** API `Buscar` por radio: `https://www.inegi.org.mx/app/api/denue/v1/consulta/Buscar/{condicion}/{lat,lon}/{metros}/{token}` con condición `todos` y radio de 700 m. El token personal sale de `DENUE_TOKEN` (`.env`, nunca versionado ni escrito en archivos o logs).

**Descarga.** Una sola, el 2026-10-29 (`fecha_consulta`), con `uv run python -m pipeline.denue`. La demo no consulta en vivo. Llamadas secuenciales con pausa de 0.25 s y tope de 600 consultas. Se consulta desde el centro de cada colonia de `data/raw/colonias_prioritarias.csv`: Coyoacán (09003) y Iztapalapa (09007) con todas sus colonias, y las demás alcaldías con una muestra de 8 colonias repartidas.

**Filtros** (`pipeline/denue/__main__.py`, y la regla anti-cadenas de `pipeline/negocios/filtros.py`):
- Giro: comercio al por menor y servicios de consumo cotidiano (restaurantes, cafeterías, salones de belleza, lavanderías, panificación, tortillerías, cerrajerías, veterinarias, gimnasios, fotocopiado, etc.). Se excluyen mayoreo, minisúpers, supermercados, autoservicio y tiendas departamentales.
- Estrato: "0 a 5 personas" o "6 a 10 personas".
- Sin cadenas: nombre o razón social contra `pipeline/negocios/cadenas.txt`, y nombres repetidos 5 o más veces.
- Deduplicado por `Id` (los radios se traslapan).
- Acotado (`acotar`): se descartan registros fuera de la CDMX (el radio de 700 m cruza a Nezahualcóyotl, Naucalpan, etc.); Coyoacán e Iztapalapa se conservan completas y las otras 14 alcaldías se reducen a una muestra repartida de 300 negocios cada una.

**Resultado (2026-10-29).** 558 consultas (completa, sin truncar por tiempo ni tope), 210,378 establecimientos crudos únicos, 59,871 negocios locales en `data/processed/negocios_denue.json`: Iztapalapa 43,638; Coyoacán 12,033; 14 alcaldías restantes 300 cada una. El archivo pesa unos 18 MB.

**Campos guardados.** `id_denue`, `nombre`, `giro` (nombre de la clase de actividad), `colonia`, `lat`, `lng`, `alcaldia`, `tipo`, `tipo_dato`, `fuente`, `fecha_consulta`. No se guardan teléfonos, correos ni sitios web.

**Límites.**
- La API no devuelve la clave SCIAN, solo el nombre de la clase; el filtro de giro es por nombre.
- La cobertura es por círculos desde el centro de la colonia: puede haber huecos entre colonias y negocios en el borde que no entran. "Completa" significa todas las colonias de la alcaldía en el CSV, no el censo de todos sus establecimientos.
- El DENUE es un directorio: puede incluir negocios cerrados o con coordenadas aproximadas.
- Fuera de Coyoacán e Iztapalapa es una muestra, no representa la alcaldía.

**Qué sigue simulado.** `data/processed/negocios.json` (negocios simulados con forma de DENUE), ventas y transacciones, programas y cualquier dato de la demo que no esté en `negocios_denue.json`.

**Pruebas.** `pipeline/tests/test_denue.py` corre sin red con `pipeline/tests/muestras/denue.json` (muestra grabada, sin token ni datos de contacto).
