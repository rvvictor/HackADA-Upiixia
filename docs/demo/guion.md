# Guion de la demo (3 minutos)

**Frase del wow (IDEA-v2.md §0):** *"Una nota de voz da de alta un negocio y a su repartidor; el negocio aparece en el mapa de la ciudad y el repartidor ve su primera ruta en el portal."*

## Antes de empezar (1 min, fuera del tiempo)

```bash
DEMO_MODE=1 bash scripts/demo.sh          # sin red ni llaves; abre http://127.0.0.1:8000
```
Al final imprime `REPARTIDOR R-xxxxx · código nnnnnn`. **Apúntalos**: el código vence en 10 min y se gasta al entrar; para uno nuevo corre `uv run python scripts/simular_repartidor.py --url http://127.0.0.1:8000`.
Importante: la simulación de ofertas escribe `data/live/ofertas.jsonl` (no hay endpoint para crearlas), así que **`simular_repartidor.py` debe correr en la misma máquina que la API**. Contra el sitio de Render no sirve.
Ventana a 1280x720 o más. Pestañas abiertas: `#/inicio`, `#/mapa`, `#/negocio`, `#/usuario`, `#/repartidor`.

## Paso a paso

| Tiempo | Qué haces | Qué se ve |
|---|---|---|
| 0:00 | Abre `http://127.0.0.1:8000/#/inicio`. Di la frase del wow. | Portada colonIA: problema, cómo funciona, para quién, escala (2 alcaldías encendidas de 16). |
| 0:25 | Clic en **Mapa**. Clic en las capas **Oferta barrial**, **Impulso**, **Rutas**, y vuelve a **Actividad**. | Una capa a la vez; leyenda abajo a la derecha con `tipo_dato` y fuente de cada cifra. |
| 0:50 | Chips **Tianguis / Mercado / Negocio local**: apaga y enciende uno. Selector **Alcaldía**: Iztapalapa y de vuelta a Coyoacán. | Los puntos del tipo aparecen y desaparecen. La tarjeta de alcaldía muestra 137 tianguis y 24 mercados en Coyoacán, dato real, y la gráfica CNBV marcada Simulado. |
| 1:10 | **Alta del negocio (plan B de la nota de voz).** En terminal: `uv run python scripts/simular_alta.py --caso dona-lupe --url http://127.0.0.1:8000`. | Imprime `ALTA alta-puesto-de-dona-lupe-NNNN · h3 … · página /n/…`. Con Telegram real: manda la nota de voz al bot y pasa lo mismo. |
| 1:25 | Clic en **Negocio** y elige "Puesto de Doña Lupe · alta nueva" (arriba de la lista). | La ficha extraída (giro, productos, horario, pagos) del negocio recién dado de alta. En **Mapa** el contador "Altas hoy" sube. |
| 1:45 | Clic en **Vecina**. Escribe `2 kilos de jitomate, tortillas y pan` y **Armar mi ruta**. | Resumen: 0 cadenas, ~1.5 km a pie, 3 paradas, primera parada Puesto de Doña Lupe. Ruta solo por negocios de barrio. |
| 2:05 | Clic en **Repartidor**. Escribe el número (`R-xxxxx`) y el código de 6 dígitos que imprimió `simular_repartidor.py`. **Entrar**. | Portal de repartidores con la lista **Ofertas (n)**: tipo de negocio, colonia de salida, paradas, km, minutos y pago estimado marcado Simulado. |
| 2:20 | **Tomar ruta** en la primera oferta. Luego **Marcar como completada**. | La oferta pasa a **Mis rutas** (En curso) y luego Completada. |
| 2:40 | Pestaña **Incentivos**. | La bici destacada y la barra "te faltan X rutas". Cierra con: "el dinero se queda en la colonia". |

## Si falla X, haz Y

| Falla | Haz |
|---|---|
| Sin red (Wi-Fi caído) | `DEMO_MODE=1` ya no necesita red ni llaves: respuestas grabadas. El mapa base de Mapbox no carga (ver siguiente fila), el resto sigue. |
| Sin llave de Mapbox (`VITE_MAPBOX_TOKEN` no estaba en el build) | El mapa muestra "El mapa necesita una llave de Mapbox". El panel derecho, las capas, la tarjeta de alcaldía, la ruta de la vecina (aproximada en línea recta) y el portal siguen funcionando. Narra sobre el panel y las cifras. Si hay llave, ponla en `.env` y reconstruye (`npm --prefix web run build`). |
| API caída o error 500 | Reinicia `DEMO_MODE=1 bash scripts/demo.sh`. Si no revive: abre el video `docs/plan-b/colonia-demo-completo.mp4` y narra encima. |
| API de repartidores no responde | El portal cambia solo a datos de ejemplo (etiqueta Simulado): puedes entrar con cualquier número `R-12345` y código de 6 dígitos y recorrer ofertas, tomar, completar e incentivos. |
| El código del repartidor venció o ya se usó | Corre otra vez `simular_repartidor.py --url …` y usa el nuevo par. |
| "Ofertas (0)" (ya se tomaron todas) | Las ofertas tienen id fijo: tomadas no vuelven. Borra `data/live/ofertas.jsonl` y vuelve a correr `simular_repartidor.py`. |
| Render dormido (plan free, tarda ~1 min tras 15 min inactivo) | Abre https://colonia-hackada.onrender.com 2 min antes. Es solo lectura: las simulaciones de alta y de repartidor van en la máquina local. |
| No hay Telegram | Es el plan B por diseño: `scripts/simular_alta.py`. |
