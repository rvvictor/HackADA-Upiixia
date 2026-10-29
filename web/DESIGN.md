# DESIGN · colonIA

> Owner: PB-029. Tokens live in `web/src/lib/ui/tokens.css`; components in `web/src/lib/ui/`; the map in `web/src/lib/map/`.

## 1. Principios

1. **La ciudad es la protagonista.** El mapa y los datos ocupan el espacio; la interfaz es un marco editorial y limpio.
2. **Cada cifra dice qué es.** Junto a todo número va una `Etiqueta` (real · estimado · simulado) con su fuente. `Cifra` ya la incluye.
3. **Un color de marca.** Rosa mexicano para la marca y la acción principal; cempasúchil para el impulso; jade para lo real; añil para lo estimado. Nada de gradientes morados genéricos.
4. **Se lee desde el fondo de la sala y la usa una persona mayor.** Texto base 18 px, controles ≥ 48 px, contraste AA, foco siempre visible, lenguaje claro.
5. **Motivo hexagonal.** La rejilla H3 del mapa es también la textura (`PatronHex`) y la marca (`MarcaHex`).

## 2. Color

| Token | Valor | Uso |
|---|---|---|
| `--pb-fondo` / `--pb-superficie` / `--pb-superficie-2` | `#f6f7f4` / `#ffffff` / `#eef0ec` | página, tarjetas, zonas hundidas |
| `--pb-texto` / `--pb-texto-2` | `#0e1116` / `#4a5160` | texto (17.6:1 y 7.4:1 sobre fondo) |
| `--pb-marca` | `#e6007e` | logo, titulares grandes (no texto chico) |
| `--pb-acento` / `-fuerte` / `-suave` | `#c8006e` / `#a80058` / `#ffe3f1` | botón primario (5.7:1 con blanco), hover, chip activo |
| `--pb-cempasuchil` · `--pb-jade` · `--pb-anil` | `#ffb703` · `#00a86b` · `#1f3b8c` | impulso, dato real, estimado / foco |
| Etiquetas | real `#006b45/#ddf5ea` · estimado `#1f3b8c/#e3e9fa` · simulado `#3d4651/#eceef1` | todas ≥ 5.7:1; simulado además punteado |
| Rampa actividad | `#e3f2ee → #a7dccb → #4fb89a → #1d8a80 → #1f3b8c` | altura/color del mapa |
| Rampa impulso | `#fff4d6 → #ffd166 → #ffb703 → #f26a2e → #c8006e` | dónde hace falta comercio |
| Hero oscuro | `--pb-hero-fondo #0b0f14`, `--pb-hero-superficie`, `--pb-hero-texto(-2)`, `--pb-hero-brillo` | landing y momentos de presentación |

## 3. Tipografía

- Display: **Bricolage Grotesque Variable** (`.pb-display` o `var(--pb-font-display)`), 700–800, tracking −0.03em, interlineado 0.95. Titulares de 40–96 px.
- Texto: **Geist Variable**, base 18 px. Cifras siempre con `.pb-cifra` (números tabulares).
- Antetítulos: 14 px, mayúsculas, tracking 0.14em, en rosa.

## 4. Forma, profundidad y espacio

- Radios: controles y chips `rounded-full`; tarjetas `--pb-radio-tarjeta` (20 px); bloques grandes `--pb-radio-grande` (28 px).
- Sombras: `--pb-sombra` (reposo), `--pb-sombra-alta` (hover/flotante), `--pb-sombra-marca` (botón primario).
- Paneles sobre el mapa: `.pb-vidrio` (blanco 78% + blur).
- Espacio generoso: secciones de 64–96 px verticales; máximo 1152 px de ancho de lectura.

## 5. Componentes (`web/src/lib/ui/`)

| Componente | Para qué |
|---|---|
| `Boton` | `primario` (uno por pantalla), `secundario`, `fantasma`, `oscuro`; `tamano` md/lg; píldora |
| `Tarjeta` | superficie con `antetitulo`, `titulo`, `accion`; `variante` normal/elevada/plana |
| `Chip` | etiqueta estática (`tono` neutro/marca/exito) o toggle con `onClick` |
| `Etiqueta` | real · estimado · simulado, junto a toda cifra |
| `Cifra` | número grande que cuenta al aparecer o cambiar, con etiqueta y tipo de dato |
| `Logo` / `MarcaHex` | colonIA con "IA" en rosa; marca de 3 hexágonos |
| `PatronHex` | textura de hexágonos para fondos (decorativa, `aria-hidden`) |
| `Seccion` | bloque editorial con antetítulo, título display y descripción; `oscuro` para el hero |
| `MapaBase` (`lib/map`) | Mapbox con `estilo` "claro" u "oscuro"; aviso claro sin token o sin WebGL |

## 6. Movimiento

- `motion`: entradas escalonadas de 40–60 ms, curva `[0.16, 1, 0.3, 1]`, 300–600 ms; contadores de 0.9 s; hover con elevación de 2 px.
- Siempre respetar `prefers-reduced-motion` (los tokens ya lo apagan en CSS; en JS usa `useReducedMotion`).

## 7. Prohibido

- Texto chico en `--pb-marca` sobre blanco (usa `--pb-acento`).
- Una cifra sin `Etiqueta`. Colores fuera de los tokens. Emojis como iconos (usa Phosphor).
- Gradientes morados genéricos, glassmorphism en todo, sombras duras.
