#!/usr/bin/env bash
# colonIA en un solo proceso para la demo: construye el web, levanta FastAPI en :8000 y, si hay token, el bot.
#   bash scripts/demo.sh            # con llaves del archivo de entorno (OpenAI, Mapbox, Telegram)
#   DEMO_MODE=1 bash scripts/demo.sh   # sin internet ni llaves: respuestas grabadas (plan B)
# Luego abre http://127.0.0.1:8000  ·  plan B del alta: uv run python scripts/simular_alta.py --caso dona-lupe --url http://127.0.0.1:8000
set -eu
cd "$(dirname "$0")/.."
PORT=${PORT:-8000}

uv sync --quiet
[ -f data/demo/plataforma_simulada.json ] || uv run python scripts/generar_historia.py
npm --prefix web ci --prefer-offline --no-audit --no-fund --loglevel=error
npm --prefix web run build

pids=""
trap 'kill $pids 2>/dev/null || true' EXIT INT TERM

uv run uvicorn app.main:app --host 127.0.0.1 --port "$PORT" &
pids="$pids $!"

# The bot reads TELEGRAM_BOT_TOKEN through app/config.py; without it (or in DEMO_MODE) it is skipped.
if [ "${DEMO_MODE:-0}" != 1 ] && uv run python -c 'from app.config import settings; raise SystemExit(0 if settings.telegram_bot_token else 1)'; then
  uv run python -m app.bot &
  pids="$pids $!"
  echo "Bot de Telegram en marcha (long polling)."
else
  echo "Bot de Telegram apagado (sin token o DEMO_MODE=1). Plan B: scripts/simular_alta.py"
fi

echo "colonIA: http://127.0.0.1:$PORT  (SEDECO #/sedeco · Vecina #/usuario · Negocio #/negocio)"
wait
