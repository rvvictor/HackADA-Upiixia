# Fuente: geografía, población, dinero CNBV y tianguis (demo)

Generador: `pipeline/geo/` · comando: `uv run python -m pipeline.geo` · semilla fija `20261025`.
Salidas: `data/processed/hex.geojson`, `data/processed/tianguis_abierto.json`, `data/processed/cnbv_tpv_municipios.json`.

## Qué es simulado (tipo_dato "simulado")

| Dato | Dónde | Cómo se simuló |
|---|---|---|
| Polígonos de Coyoacán (09003) e Iztapalapa (09007) | `pipeline/geo/zonas.py` | Contornos escritos a mano, aproximados. No son el Marco Geoestadístico. |
| Población por hexágono (`poblacion`) | `hex.geojson` | Totales de zona inventados (orden de magnitud, no cifras oficiales) repartidos con pesos aleatorios y más densidad hacia el centro. |
| `negocios_total`, `negocios_barriales` | `hex.geojson` | Ligados a la población (1 negocio por 60 personas en Coyoacán, por 110 en Iztapalapa) con ruido. No son DENUE. |
| Totales TPV por alcaldía (`transacciones_tpv`, `monto_tpv`, `adultos`) | `cnbv_tpv_municipios.json` | Inventados. Iztapalapa tiene más población pero menos transacciones por adulto que Coyoacán. |
| `actividad_tpv_est` por hexágono | `hex.geojson` | Reparto proporcional del total simulado de la alcaldía. La suma por alcaldía coincide con el total (±0.5%). |
| `monto_est` | `hex.geojson` | `null`: no hay ticket promedio real de Banxico en esta versión. |
| Tianguis y mercados (~60) | `tianguis_abierto.json` | Nombres, colonias, coordenadas, días y horarios inventados. Giros, productos y formas de pago inventados. |
| `periodo_cnbv` = `2023-T2` | todos | Marcador. No es un trimestre verificado. |
| `fuente_url` / `fecha_descarga` en CNBV | `cnbv_tpv_municipios.json` | `null`. No se inventó ninguna URL. |

Cómo se calculan los derivados (Apéndice A.3):
- `impulso = rank_pob × (1 − rank_act)` si `negocios_barriales ≥ 1`, si no `0`. Los rangos son percentiles sobre todos los hexágonos de la zona.
- `oculto = negocios_total < 3`.
- `cluster_id`: componentes conexas por vecinos H3 entre hexágonos con `negocios_barriales ≥ 8`. Los demás quedan en `null`.

Etiquetas de `tipo_campos`: los insumos simulados van como `simulado`; los índices calculados (`impulso`, `oculto`, `cluster_id`, `monto_est`) van como `estimado`.

Días de la semana en `dias`: 0 = lunes … 6 = domingo.

## Qué es real

Nada en estos archivos es un dato oficial todavía. La única excepción posible son las filas de `data/campo/tianguis_verificados.csv` (si existe), que salen con `tipo_dato: "real"`, `fuente` y `verificado_por` de la hoja de campo. El CSV no existe en el repo aún.

Columnas que lee el generador: `nombre, alcaldia_cvegeo, lat, lng, dias, abre, cierra` (obligatorias); `id, tipo, colonia, giros, productos, formas_pago, acepta_mercomuna, fuente, fecha_verificacion, verificado_por` (opcionales). Listas separadas por `|` o `;`. `dias` 0–6. El CSV sustituye filas simuladas: el total se mantiene en 60.

## Qué fuente real reemplaza cada parte

| Simulado | Fuente real | Notas |
|---|---|---|
| Polígonos | Marco Geoestadístico INEGI, capa municipal (09003, 09007) | Reemplazar `zonas.py` por la capa oficial. |
| Población por hexágono | Censo 2020 INEGI, AGEB + centroides | Agregar `pob_total` por AGEB y asignar cada uno a su H3. |
| `negocios_*` por hexágono | DENUE INEGI (términos de libre uso) | Contar establecimientos barriales por hexágono; ver PB-005. |
| Transacciones, monto y adultos TPV | CNBV, Bases de Datos de Inclusión Financiera (BDIF) | Último trimestre disponible; sustituir `periodo_cnbv`. Adultos: Censo 2020. |
| Ticket promedio (`monto_est`) | Banxico SIE | Solo si hay serie y token; si no, queda `null`. |
| Tianguis y mercados | SEDECO, tianguis y mercados (datos abiertos CDMX) + levantamiento de campo | Campo con `data/campo/tianguis_verificados.csv`. |

Mientras la fuente real no esté, cualquier cifra que salga de estos archivos debe mostrarse con su etiqueta `simulado`. Nunca como dato real.

## Bolsa de poco movimiento junto a la sede (ajuste de demo)

Los hexágonos a ≤ 1.3 km del centro de la demo (19.3476, -99.1574) reciben más peso de población (×2) y
menos peso de actividad TPV (×0.15) **dentro del dato simulado**, renormalizado por alcaldía (los totales
no cambian). Es una decisión deliberada para contar la historia de la demo (Karla vive en una zona con
mucha gente y poco movimiento de pago digital); **no es un hallazgo**. Con datos reales (CNBV + DENUE)
esta bolsa desaparece y el mapa muestra lo que diga el dato.
