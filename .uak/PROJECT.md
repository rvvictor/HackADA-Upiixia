# PROJECT · HackADA · colonIA (sprint mode)

> Filled in by `/uak-setup` with the human at minute 0. uak reads the flat fields of the last block from
> the remote `main`, so a stale worktree can never change permissions.

## Event
| Field | Value |
|---|---|
| Event / challenge | HackADA · challenge: Mercaditos locales (comercio de proximidad y redes comunitarias de distribución): herramienta de IA que conecta mercados públicos, tianguis y pequeños comercios con consumidores y repartidores locales (catálogos digitales, pedidos, rutas de entrega, distribución comunitaria, análisis de demanda local) · goal: fortalecer circuitos económicos de proximidad, subir ventas de pequeños comerciantes y que el valor económico circule dentro de las comunidades · product name: **colonIA** (ya no Pulso Barrial) |
| Start | 2026-10-29 13:00 America/Mexico_City |
| Official deadline | 2026-10-29 16:00 America/Mexico_City (moved from 15:00) · platforms: form link not announced yet (TBD) |
| Freeze | 2026-10-29 15:30 (Freeze-Epoch 1793309400) · plan-B video 14:30 |
| Clean rehearsal / plan B | 15:40 |
| Internal submission | 15:45 |
| Humans | Cris, Yojan, Victor, Zoe · submission owner: Victor |
| Agents | cris-1, cris-2, yojan-1, yojan-2, victor-1, victor-2, zoe-1, zoe-2 (all Claude Code) |
| Machines | `<laptop, Jetson…>` · ports already taken: `<8000…>` |

## Official rubric (weights sum to 100)
Source: photo of the official sheet (4 criteria, 25 points each).
| ID | Criterion | Weight | Evidence in the demo |
|---|---|---:|---|
| C1 | Núcleo funcional en una hora: el flujo principal funciona de punta a punta | 25 | live demo of the main flow, working from the first hour |
| C2 | Uso inteligente de IA | 25 | the AI flow on screen: where the model decides something a rule could not; initial prompt shown |
| C3 | Trazabilidad de datos: de dónde sale cada dato y qué es real, estimado o simulado | 25 | every figure carries its source and `tipo_dato` label |
| C4 | Diseño de experiencia | 25 | plain Spanish UI, large text, clear flow for each role (comerciante, consumidor, repartidor) |

Required deliverables (from the sheet): prototipo, demo, README, datos o estructura propuesta, prompt inicial, flujo de IA, cuello de botella, ficha de impacto económico y ruta de maduración a 30 días.

## Event rules
| Topic | Confirmed rule | Source |
|---|---|---|
| AI use / prior code | AI allowed · prior code: reuse of the Chilangatón base (Pulso Barrial) by the team; nothing new announced | team |
| Data and licenses | TBD | - |
| Format and video limits | TBD (nothing special announced) | - |

## Plan B
- A video of the whole flow at `docs/plan-b/colonia.mp4` (v1 at 14:00, final at 14:30). Use it if the network, the mic or an external API fails.

## Executable config
A human sets `yes`. A missing field means `no`.

```text
Mode: sprint
Backlog-Proposed-Epoch: 0
Backlog-Approved: no
Autonomy: yes
Auto-Merge: yes
Review-Mode: claims
Plan-Channel: claims
Freeze-Epoch: 1793309400
Lease-Seconds: 2700
Review-Lease-Seconds: 14400
Events-Per-Session: 100
Checkpoint-Percent: 60
Merge-Lease-Seconds: 1800
Merge-Wait-Seconds: 180
Max-Parallel-Subagents: 4
Opus-Subagents-Per-Session: 2
Pace: auto
Subagent-Hard-Cap: 6
Strong-Hard-Cap: 3
Subagents-Per-Session: 40
Subagents-Per-Machine: 8
Subagent-Burst-Per-Minute: 6
Max-Worktree-Agents: 6
Blackbox: on
Additive-Paths: -
```
