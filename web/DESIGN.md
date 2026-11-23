# DESIGN · colonIA · Dirección C "Maqueta viva"

> Owner: CO-028. Elegida por cris viendo capturas (`uak decision CO-028`, 2026-11-23); paleta rosa mexicano y
> sin etiquetas real/simulado en pantalla por decisión posterior de cris (misma tarea). Un cambio global de tema,
> paleta o tipografía necesita otra `uak decision` aprobada por un humano.
> Tokens: `web/src/lib/ui/tokens.css`. Componentes: `web/src/lib/ui/`. Mapa: `web/src/lib/map/`.
> Referencias: `web/public/design-lock/C.html` (la propuesta, aún en cobalto y con etiquetas: manda este archivo)
> y `web/public/design-lock/screens/pantalla-*.png` (capturas fijadas de la app real).

## 1. La idea

La ciudad como **maqueta de arquitecto**: bloques blancos sobre un suelo de concreto frío, **rosa mexicano** donde
falta comercio y **pines de tinta** para los tianguis. El dato manda: el titular cambia con el día, la altura es
actividad y el color es impulso. La interfaz es el marco; la maqueta es la protagonista.

1. **La ciudad es la protagonista.** Mapa y maqueta ocupan el espacio; los paneles flotan encima, blancos y planos.
2. **Un solo color.** Rosa mexicano para acción, marca y "falta comercio". Todo lo demás es concreto y tinta.
3. **Se lee desde el fondo de la sala y la usa una persona mayor.** Texto base 18 px, controles de 48 px o más,
   contraste AA, foco siempre visible, español claro.
4. **El texto responde al dato.** Cuando el usuario elige algo (día, hora, alcaldía), el titular o la cifra principal
   lo dice en palabras: "Así late Coyoacán el domingo".

## 2. Color (`tokens.css`)

| Token | Valor | Uso |
|---|---|---|
| `--pb-fondo` / `--pb-suelo` | `#eef0f3` / `#dfe3e8` | página; suelo de la maqueta y zonas hundidas |
| `--pb-superficie` / `--pb-superficie-2` | `#ffffff` / `#e6e9ed` | paneles y tarjetas; hover y pistas |
| `--pb-texto` / `--pb-texto-2` | `#14171c` / `#4b5360` | texto (16.9:1 y 7.0:1 sobre fondo) |
| `--pb-borde` / `--pb-borde-fuerte` | `#d3d8de` / `#7c8390` | bordes de panel; bordes de control |
| `--pb-acento` / `-fuerte` / `-suave` | `#c8006a` / `#a00055` / `#fbe3ef` | botón primario (5.7:1 con blanco), hover, pestaña activa |
| `--pb-marca` | `#d1006c` | "IA" del logo y titulares grandes |
| `--pb-pin` | `#14171c` | pines de tianguis sobre bloques rosa |
| `--pb-jade` / `--pb-error` | `#2f7a5a` / `#b42318` | solo estados de éxito y error |
| Rampa actividad (altura) | `#f4f5f7 → #d9dde3 → #b3bac4 → #7c8390 → #3a414c` | bloques: de blanco a tinta |
| Rampa impulso (color) | `#faf3f6 → #f3d2e2 → #e693bb → #d6438a → #b0005a` | tapas de los bloques: de blanco a rosa |
| Oscuro | `--pb-hero-fondo #14171c`, `--pb-hero-superficie #20242b` | solo momentos de presentación |

Nombres viejos conservados para no romper vistas: `--pb-cempasuchil` y `--pb-anil` ahora caen en la familia rosa.

## 3. Tipografía

- **Display:** Bricolage Grotesque Variable (autoalojada en `lib/ui/fonts/`, OFL), 800, tracking −0.045em,
  interlineado 0.98. Clase `.pb-display`. Titulares de 40 a 64 px; cifras grandes de 32 a 64 px.
- **Texto:** Geist Variable, base 18 px. Cifras con `.pb-cifra` (números tabulares).
- Énfasis dentro de un titular: la palabra que cambia con el dato va en `--pb-acento`, misma familia y peso.

## 4. Forma, profundidad y espacio

- Radios: controles y pestañas `rounded-full`; paneles `--pb-radio-tarjeta` (20 px); bloques grandes 28 px.
- Sombras largas y suaves como una maqueta bajo una lámpara (`--pb-sombra-alta`); nunca halos ni brillos.
- Paneles sobre el mapa: blancos al 86 % (`.pb-vidrio`), borde `--pb-borde`.
- Navegación: barra superior de 68 px en escritorio; en teléfono las vistas bajan a una barra inferior con ícono
  y texto (una mano). Contenedor de lectura de 1280 px con márgenes de 16 px (teléfono) y 32 px (md).

## 5. Componentes (`web/src/lib/ui/`)

| Componente | Para qué |
|---|---|
| `AppShell` | marco de toda vista: `NavBar` + `main` que llena la pantalla; lo usa `App.tsx` |
| `NavBar` | logo + pestañas en escritorio; barra inferior con íconos Phosphor en teléfono |
| `PageLayout` | `ancho="lectura"` (columna de 1280 px) o `ancho="lleno"` (mapas a sangre) |
| `PageHeader` | titular display, una línea de descripción y acciones (un solo primario) |
| `Boton` | `primario` (uno por pantalla), `secundario`, `fantasma`, `oscuro`; píldora; 3 palabras o menos |
| `Tarjeta`, `Chip`, `Seccion` | superficie con encabezado; chip estático o interruptor; bloque editorial |
| `Cifra` | número grande que cuenta al aparecer, con su texto debajo |
| `Etiqueta` | chip real · estimado · simulado. **Apagado** (`MOSTRAR_TIPO_DATO = false`): no dibuja nada |
| `Logo` / `MarcaHex` | colonIA con "IA" en rosa; marca de 3 hexágonos (rosa, rosa claro, tinta) |
| `MapaBase` (`lib/map`) | Mapbox; aviso claro sin llave o sin WebGL |

## 6. Recetas por pantalla

| Pantalla | Ruta | Receta | Hero (lo primero que se ve, sin scroll a 1280×720) |
|---|---|---|---|
| Inicio | `#/inicio` (y `#/`) | landing | la maqueta viva con la cifra de negocios dados de alta y un llamado a `#/mapa` |
| Mapa SEDECO | `#/mapa` (`#/sedeco` redirige) | map + panel | la ciudad con la altura de los hexágonos; panel con día, hora y la cifra de actividad |
| Vecina | `#/usuario` | flow | la ruta dibujada sobre el mapa con sus paradas; 3 pasos claros |
| Negocio | `#/negocio/:id` | detail | la ficha del negocio recién dado de alta con el repartidor de su colonia |
| Repartidor | `#/repartidor` | map + panel / list | el mapa de ofertas con la primera ruta resaltada; incentivos como lista con la bici arriba |

- **landing:** titular display a la izquierda, maqueta a la derecha a sangre; una cifra, un primario.
- **map + panel:** mapa lleno (`PageLayout ancho="lleno"`), panel blanco a la derecha de 360 a 400 px; en teléfono el
  panel es una hoja inferior.
- **flow:** pasos numerados en una columna; el resultado (mapa o ficha) a la derecha en escritorio, abajo en teléfono.
- **detail:** encabezado con nombre y acción, luego bloques de datos en rejilla de 2 columnas (1 en teléfono).
- **list:** la tarjeta principal grande arriba, las demás en filas con espacio, sin bordes en cada fila.
- **dashboard** (gráficas de crecimiento): series en tonos de la rampa impulso, ejes en `--pb-texto-2`, fuente debajo.

## 7. Movimiento

- `motion`: entradas de 300 a 600 ms con curva `[0.16, 1, 0.3, 1]`; pines que aparecen al cambiar el día; contadores
  de 0.9 s; hover con elevación de 2 px.
- Todo respeta `prefers-reduced-motion` (los tokens lo apagan en CSS; en JS usa `useReducedMotion`).

## 8. Nunca

1. **Nunca un segundo color de acento.** Nada de azul, verde o naranja para acciones o rampas; el rosa es el único.
2. **Nunca chips de real · estimado · simulado en pantalla** mientras `MOSTRAR_TIPO_DATO` sea `false`; tampoco
   escribirlos a mano en leyendas. El dato sigue llevando `tipo_dato` y `fuente` en la API.
3. **Nunca texto chico en `--pb-marca` sobre blanco** (usa `--pb-acento-fuerte`), ni emojis como íconos (usa
   Phosphor), ni gradientes morados, halos o glassmorphism en todo.
