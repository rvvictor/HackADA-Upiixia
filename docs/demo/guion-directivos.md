# Guion de 5 minutos para directivos

**Frase del wow:** *"Una nota de voz da de alta un negocio de barrio; aparece en el mapa de la ciudad y el repartidor de su colonia ve su primera ruta."*

Para quién: directivos (SEDECO, alcaldías, CANACOPE). Tono: problema concreto, una pantalla a la vez, cada cifra con su fuente dicha en voz alta.

## Antes de entrar a la sala (fuera del tiempo)

```bash
git clone git@github.com:rvvictor/HackADA-Upiixia.git colonia-demo && cd colonia-demo
DEMO_MODE=1 bash scripts/demo.sh        # sin red ni llaves; abre http://127.0.0.1:8000
```

- Ventana a 1280×720 o más, zoom del navegador al 100 %.
- Si hay llave de Mapbox: `VITE_MAPBOX_TOKEN` en el `.env` de la raíz (Vite lo lee desde ahí, CO-041) **antes** de correr `demo.sh`. Sin llave el mapa base muestra un aviso y todo lo demás funciona.
- Deja abierta una terminal en la carpeta del repo para el alta de Doña Lupe.

## Paso a paso (5:00)

| Tiempo | Qué haces | Qué dices | Qué se ve |
|---|---|---|---|
| 0:00 | Abre `#/inicio`. | La frase del wow. "En la CDMX hay 1,367 tianguis y casi ninguno aparece junto en un mapa vivo." | Portada colonIA con la maqueta de la ciudad. |
| 0:30 | Clic en **Mapa**. | "Cada hexágono es un pedazo de ciudad. La altura es la actividad de pago con tarjeta; el color rosa es dónde falta comercio de barrio." | Mapa SEDECO; a la derecha "El *día* a las *hora*" y la cifra de tianguis abiertos. |
| 1:00 | En el panel elige **dom** y luego **mar**. | "El domingo abren más tianguis; el martes se apagan y aparecen los huecos. Esa es la decisión que hoy se toma sin datos." | Cambia la cifra de tianguis abiertos y la gente cubierta a 800 m; el titular dice el día. |
| 1:30 | En **Alcaldía**: Coyoacán → **Ver detalle**. | "Coyoacán: 137 tianguis y 24 mercados, de datos abiertos de la CDMX. Abajo, la serie de pagos con tarjeta de la CNBV." | Tarjeta de alcaldía con su gráfica y la fuente debajo. |
| 2:00 | En la terminal: `uv run python scripts/simular_alta.py --caso dona-lupe --url http://127.0.0.1:8000`. (Con Telegram real: la nota de voz al bot.) | "Doña Lupe no llenó ningún formulario: mandó una nota de voz. La IA solo extrae los campos; las cifras y la ruta las calcula código." | `ALTA alta-puesto-de-dona-lupe …` en la terminal; en **Mapa** sube "Negocios dados de alta hoy". |
| 2:30 | Clic en **Negocio** → "Puesto de Doña Lupe · alta nueva". Toca **Agregar mi colonia**, escribe `San Lucas`, **Guardar cambios**. | "Esta es su ficha, sacada de su voz, y la puede corregir. En cuanto dice su colonia, aparece el repartidor de su barrio." | Ficha editable; la tarjeta "Tu repartidor de la colonia" muestra al repartidor de San Lucas. |
| 3:15 | Clic en **Vecina** → **Armar mi ruta** (la lista ya viene escrita). | "Karla, vecina de Coyoacán, escribe su mandado. La ruta pasa solo por negocios de barrio: cero cadenas." | Paso 2: "0 cadenas", km y minutos; paso 3: las paradas, cada una dice por qué fue elegida. |
| 3:45 | Clic en **Repartidor** → **Entrar** (número `R-00001` ya escrito). | "El repartidor de la misma colonia ve sus ofertas en el mapa. La primera ruta ya viene resaltada." | Portal con la primera oferta resaltada en rosa. |
| 4:15 | **Tomar ruta** → pestaña **Premios**. | "Con rutas cortas en su barrio se acerca a la bici. El dinero se queda en la colonia." | "Te faltan *N* rutas para tu bici" con la barra. |
| 4:40 | Vuelve a **Mapa**. | Cierre: "Lo que ya existe en la calle, ahora visible, medible y conectado. Encender otra alcaldía es cambiar un parámetro." | Mapa con el alta de hoy contada. |

## Plan B sin red

1. `DEMO_MODE=1` no necesita internet ni llaves: la IA, Mapbox y Telegram responden con datos grabados (`app/fixtures/`).
2. Sin llave de Mapbox el mapa base muestra "El mapa necesita una llave de Mapbox"; narra sobre el panel (día, hora, cifra), la tarjeta de alcaldía, la ficha, la ruta (aproximada en línea recta) y el portal.
3. Si la API se cae: reinicia `DEMO_MODE=1 bash scripts/demo.sh`. Si no revive, abre el video `docs/plan-b/colonia-demo-completo.mp4` y narra encima.
4. Sin Telegram: `scripts/simular_alta.py` es el alta por diseño.
5. La app en Render (https://colonia-hackada.onrender.com) duerme en el plan gratis; ábrela 2 minutos antes y úsala solo para mostrar, no para dar de alta.

## Lo que NO prometemos

- **Cifras simuladas.** La población por hexágono, los negocios por hexágono, la actividad de pago por hexágono, las ventas, el avance del negocio y los premios del repartidor son **simulados o calculados** para la demo. En pantalla ya no lleva etiqueta (decisión de cris, CO-028), así que **dilo en voz alta** si alguien pregunta; la API conserva `tipo_dato` y `fuente` en cada cifra.
- **Reales:** 1,367 tianguis y 329 mercados (datos abiertos CDMX), 1,543 colonias, marginación CONAPO 2020, negocios DENUE y la serie CNBV por alcaldía.
- **Sin llaves no hay mapa base ni nota de voz real**: la demo usa respuestas grabadas.
- **El repartidor demo (R-00001) y sus rutas fijas** son de demostración; los premios y su patrocinador están por confirmar.
- **Solo Coyoacán e Iztapalapa** tienen todas las capas; las otras 14 alcaldías se encienden con un parámetro, no están listas.
- **No hay cobro ni pagos**: el "pago aproximado" al repartidor es una estimación de ejemplo.

## Ensayo limpio

Probar este guion completo en un clon nuevo con `DEMO_MODE=1`, cronómetro en mano, y anotar aquí lo que falló y cómo se resolvió.

| Fecha | Quién | Tiempo total | Qué falló | Arreglo |
|---|---|---|---|---|
| 2026-11-23 | crismmolina-2 (agente) | 10 s automatizado (Playwright, sin narración) | Nada: 0 errores de consola; el alta de Doña Lupe aparece y la ficha muestra al repartidor de San Lucas | Falta el ensayo humano con cronómetro y narración (meta 5:00) |
| | | | | |
