# colonIA

**colonIA es una herramienta de IA que conecta tianguis, mercados y pequeños negocios de barrio de la CDMX con vecinas, vecinos y repartidores locales, para que el dinero se quede circulando en la colonia.**

> English, in one line: colonIA turns a voice note into a neighborhood business listing and a local courier sign-up (Telegram), shows it on a city map, and plans shopping routes that only pass through neighborhood businesses. The LLM extracts fields; it never produces a number you see on screen. Run it with no keys: `DEMO_MODE=1 bash scripts/demo.sh`.

Proyecto del equipo UPIIXIA para **HackADA** (reto *Mercaditos locales*: comercio de proximidad y redes comunitarias de distribución). Se construyó sobre la base de Pulso Barrial (Chilangatón 2026); lo que cambió está en `IDEA-v2.md`.

## El problema

- El comercio de barrio vende poco en línea: **6.7 %** de los negocios vendió en línea en 2023 (STyFE CDMX con datos de Censos Económicos 2024, cita en `IDEA.md` §10).
- La CDMX tiene **1,367 tianguis** y **329 mercados públicos** (tabla de abajo), pero no aparecen juntos en un mapa vivo con su oferta.
- Entregar a domicilio hoy depende de plataformas que cobran comisión; la última milla no la resuelve el barrio.
- Doña Lupe, que vende nopales y no usa apps, no va a llenar formularios.

## Qué hace

1. **Comerciante:** manda una nota de voz por Telegram; la IA extrae la ficha (nombre, giro, productos, horario, formas de pago) y el negocio aparece en el mapa y en una página web propia.
2. **Repartidor:** se da de alta por Telegram con texto o voz (en curso, CO-009 y CO-014) y verá ofertas de ruta en un portal web.
3. **Vecino:** escribe su lista del mandado y recibe una ruta a pie que pasa solo por negocios de barrio, nunca por cadenas.
4. **Mapa (SEDECO / alcaldía):** hexágonos por colonia con una capa a la vez; cada cifra lleva su `tipo_dato` y su fuente.

Regla de oro: **el modelo nunca produce una cifra que se muestre.** Rutas, prioridades y cifras son código determinista y todas llevan `tipo_dato` (`real`, `estimado` o `simulado`). Detalle en `docs/entregables/flujo_ia.md`.

## Cómo correrlo

Requisitos: `uv` (Python 3.12 o más) y Node con `npm`.

```bash
DEMO_MODE=1 bash scripts/demo.sh      # sin internet ni llaves: respuestas grabadas (plan B)
bash scripts/demo.sh                  # con llaves en .env (OpenAI, Mapbox, Telegram)
```

`scripts/demo.sh` hace `uv sync`, genera `data/demo/plataforma_simulada.json` si falta (`scripts/generar_historia.py`), construye el web (`npm --prefix web ci` y `npm --prefix web run build`) y levanta FastAPI en `http://127.0.0.1:8000` (cambia el puerto con `PORT`). Si hay `TELEGRAM_BOT_TOKEN` y no es `DEMO_MODE=1`, también arranca el bot. Pantallas: `#/sedeco` (mapa), `#/usuario` (vecina), `#/negocio` (negocio).

Plan B del alta por voz, sin Telegram:

```bash
uv run python scripts/simular_alta.py --caso dona-lupe --url http://127.0.0.1:8000
```

Pruebas del backend: `uv run pytest -q --tb=short -x` (la configuración está en `pyproject.toml`).

## Llaves necesarias

Van solo en `.env` (está en `.gitignore`; nunca se versionan). Sin ellas, `DEMO_MODE=1` funciona completo con respuestas grabadas.

| Variable | Para qué | Respaldo sin llave |
|---|---|---|
| `OPENAI_API_KEY` | Transcripción de voz y extracción estructurada | Respuestas grabadas en `app/fixtures/` |
| `MAPBOX_TOKEN` | Rutas y orden de paradas (servidor) | Vecino más cercano en Python |
| `VITE_MAPBOX_TOKEN` | Mapa base en el navegador (token público) | Mapa sin base |
| `TELEGRAM_BOT_TOKEN` | Bot de altas | `scripts/simular_alta.py` |
| `DENUE_TOKEN` | Descarga de negocios del DENUE (INEGI) en el pipeline | Datos ya procesados en `data/processed/` |

También existe `DEMO_MODE` (`1` activa el modo sin red). Los modelos se fijan en `app/config.py`.

## Stack

- **Backend:** Python 3.12, FastAPI, Pydantic, H3 (rejilla hexagonal), RapidFuzz, `python-telegram-bot`, SDK de OpenAI, `uv`.
- **Frontend:** React 19, Vite, TypeScript, Tailwind v4, Mapbox GL JS, Motion (`web/`).
- **Datos:** JSON y GeoJSON en `data/processed/`, generados por `pipeline/`.

## Estructura de carpetas

| Carpeta | Contenido |
|---|---|
| `app/` | API (`routers/`), lógica (`services/`), contrato de datos (`schemas/`), bot de Telegram (`bot/`), fixtures y pruebas |
| `web/` | Interfaz React: mapa, vecina, negocio (y, en curso, portal de repartidores) |
| `pipeline/` | Generadores y procesadores de datos (geo, negocios, artículos, datos reales) |
| `data/fuentes/` | Una ficha por fuente: qué es, de dónde sale, qué es real y qué es simulado |
| `data/processed/` | Datos listos para la app (`data/raw/` y `data/live/` no se versionan) |
| `scripts/` | `demo.sh`, `simular_alta.py`, `generar_historia.py` |
| `docs/entregables/` | Prompt inicial, flujo de IA, cuello de botella, ficha de impacto, ruta a 30 días |
| `docs/legal/` | Pendientes legales (priorización por edad y estudiante, aviso de privacidad) |
| `.uak/` | UPIIXIA Agentic Kit: tablero de tareas, reglas y comandos del equipo |

## Datos reales vs. simulados

Cada fila de datos trae `tipo_dato`. Las fichas completas están en `data/fuentes/`.

| Dato | `tipo_dato` | Notas |
|---|---|---|
| 1,367 tianguis de la CDMX (16 alcaldías) | real | `data/fuentes/tianguis.md`; sitio exacto de descarga por confirmar |
| 329 mercados públicos | real | `data/fuentes/mercados.md`; sin horarios reales (el horario por defecto está marcado) |
| 1,543 colonias (nombre, alcaldía, centroide) | real | `data/fuentes/colonias.md` |
| Marginación por colonia (CONAPO 2020) | real | Cruce parcial con el catálogo: 849 colonias |
| Nivel de contaminación por colonia | real, método por confirmar | Cruce parcial: 649 colonias |
| Negocios locales del DENUE (Coyoacán e Iztapalapa) | real | En revisión (rama `feat/co-004`, `data/fuentes/denue.md`); en `main` los 520 negocios son simulados |
| Población y negocios por hexágono | simulado | `data/fuentes/geo.md` |
| Dinero con tarjeta (CNBV) por alcaldía | simulado | Pendiente de la base real |
| Actividad de pago por hexágono | estimado (sobre dato simulado) | Reparto proporcional |
| Historial de la plataforma (búsquedas, rutas, "compré aquí") | simulado | `demo_data: true` |
| Repartidores, ofertas, incentivos y pagos de la demo | simulado | `demo_data: true`; en curso |

## UPIIXIA Agentic Kit (cómo se coordinó el equipo)

Cuatro personas (Cris, Yojan, Victor, Zoe) y ocho agentes de Claude Code trabajaron en paralelo durante unas **3 horas** (13:00 a 16:00, 29-oct-2026) con el UPIIXIA Agentic Kit 5.3, modo *sprint*:

- Un backlog de tareas verticales (`.uak/TASKS.md`, CO-001 a CO-015), cada una con criterios, rutas permitidas y un comando de verificación exacto.
- Cada tarea tiene su propia rama, su propio *worktree* y un reclamo en la rama `claims`; ningún agente edita archivos de otra tarea.
- Revisión cruzada: quien revisa nunca es quien escribió; se aprueba o rechaza un SHA concreto tras correr el `Verify`.
- Mensajes cortos entre tareas cuando cambia un contrato, y un congelamiento de código a las 15:45.

El tablero y las reglas están en `.uak/` y `AGENTS.md`.

## Entregables de la rúbrica

- Prompt inicial: `docs/entregables/prompt_inicial.md`
- Flujo de IA: `docs/entregables/flujo_ia.md`
- Cuello de botella: `docs/entregables/cuello_botella.md`
- Ficha de impacto económico: `docs/entregables/ficha_impacto.md`
- Ruta de maduración a 30 días: `docs/entregables/ruta_30_dias.md`
- Pendiente legal: `docs/legal/priorizacion.md`
