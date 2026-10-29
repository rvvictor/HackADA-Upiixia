"""Historia SIMULADA de la plataforma: 7 días de búsquedas, rutas y "compré aquí" sobre los negocios de barrio.

    uv run python scripts/generar_historia.py

Escribe data/demo/plataforma_simulada.json (mismo formato que data/live/eventos.jsonl, con demo_data: true).
Determinista (semilla fija). Nunca se presenta como dato real: cada evento lleva demo_data: true.
"""

import json
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import config  # noqa: E402

SEMILLA = 20261025
DIAS = 7
ZONA = ZoneInfo("America/Mexico_City")
HOY = datetime(2026, 10, 25, 8, 0, tzinfo=ZONA)  # día del evento: la historia termina justo antes
SALIDA = config.DEMO_DIR / "plataforma_simulada.json"


def generar() -> list[dict]:
    rng = random.Random(SEMILLA)
    negocios = json.loads((config.PROCESSED_DIR / "negocios.json").read_text(encoding="utf-8"))
    barriales = [n for n in negocios if n["es_barrial"]]
    # Los negocios cerca de la sede aparecen más, como pasaría con un piloto que arranca en San Lucas.
    pesos = [3 if abs(n["lat"] - 19.3486) < 0.01 and abs(n["lng"] + 99.153) < 0.01 else 1 for n in barriales]
    eventos = []
    for d in range(DIAS, 0, -1):
        dia = HOY - timedelta(days=d)
        fin_de_semana = dia.weekday() >= 5
        for _ in range(rng.randint(35, 55) if fin_de_semana else rng.randint(15, 30)):
            ts = (dia + timedelta(minutes=rng.randint(0, 11 * 60))).timestamp()
            eventos.append({"ts": ts, "tipo": "busqueda", "negocio_id": None, "h3": None, "demo_data": True})
            for n in rng.choices(barriales, pesos, k=rng.randint(3, 5)):
                eventos.append({"ts": ts + 1, "tipo": "aparicion_ruta", "negocio_id": n["id"], "h3": n["h3"],
                                "demo_data": True})
                if rng.random() < 0.35:
                    eventos.append({"ts": ts + rng.randint(600, 3600), "tipo": "compre_aqui", "negocio_id": n["id"],
                                    "h3": n["h3"], "demo_data": True})
                if rng.random() < 0.15:
                    eventos.append({"ts": ts + rng.randint(60, 900), "tipo": "vista_pagina", "negocio_id": n["id"],
                                    "h3": n["h3"], "demo_data": True})
    return sorted(eventos, key=lambda e: e["ts"])


def main() -> None:
    eventos = generar()
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(json.dumps(eventos, ensure_ascii=False) + "\n", encoding="utf-8")
    conteo = {t: sum(e["tipo"] == t for e in eventos) for t in ("busqueda", "aparicion_ruta", "compre_aqui", "vista_pagina")}
    print(f"plataforma_simulada.json: {len(eventos)} eventos simulados en {DIAS} días · {conteo}")


if __name__ == "__main__":
    main()
