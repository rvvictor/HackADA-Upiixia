# Checklist de entrega (`.uak/modes/sprint.md` §Submission checklist)

Verificado el 2026-10-29 ~15:45 CDMX. Corte oficial 16:00.

| Punto | Estado | Evidencia |
|---|---|---|
| Repo con código, README y llaves fuera de git | OK | `git ls-files` no contiene `.env` ni `data/raw`; `.env.example` existe. Repo: https://github.com/rvvictor/HackADA-Upiixia |
| README del producto: capturas reales, setup, variables, demo sin llaves | PARCIAL | Tiene setup (`uv sync`/`npm ci` vía demo.sh), tabla de llaves y `DEMO_MODE=1`. Está en español con una línea en inglés; **no tiene capturas** (usar `docs/plan-b/capturas/`). |
| Demo reproducible desde un clon limpio en 5 min o menos | OK | `DEMO_MODE=1 PORT=8765 bash scripts/demo.sh` en clon limpio: arriba en menos de 2 min. Ver `docs/demo/ensayo.md`. |
| Demo en vivo | OK | https://colonia-hackada.onrender.com respondió `{"status":"ok"}` (HTTP 200). Plan free: duerme tras 15 min; despertarla 2 min antes. Las simulaciones de alta y repartidor solo corren en local. |
| Guion de la demo (3 min) | OK | `docs/demo/guion.md` |
| Video plan B | OK | `docs/plan-b/colonia-demo-completo.mp4` (0.46 MB) y `.webm`; ver limitaciones en `docs/plan-b/README.md` |
| Videos dentro de los límites del evento | POR VERIFICAR | El video plan B dura 34 s; confirmar el límite y si el formulario pide un video propio. |
| Licencias de datos y librerías declaradas | POR VERIFICAR | El README no menciona licencias; hay `docs/legal/`. Revisar que las no comerciales estén explícitas. |
| Envío en TODAS las plataformas que pide el evento, con comprobante | PENDIENTE | Formulario: **por agregar** (el link aún no existe). Guardar el comprobante en cuanto se envíe. |
| `/uak-retro` dentro de 48 h | PENDIENTE | Después del evento. |

## Fallos conocidos de la demo (ver `docs/demo/ensayo.md`)
Sin llave de Mapbox no hay mapa base; con la API real "Mis rutas" del repartidor queda vacío (completar e incentivos solo funcionan en modo mock).
