"""Plan B de la demo: inyecta el alta de Doña Lupe sin Telegram ni internet.

    uv run python scripts/simular_alta.py --caso dona-lupe
    uv run python scripts/simular_alta.py --caso dona-lupe --url http://127.0.0.1:8000   # vía la API en marcha
"""

import argparse
import json
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services import altas

# A ~100 m de SEDE (19.3486, -99.153): el origen por defecto de la vista Vecina y de /api/ruta, para que la
# ruta de la demo pase por su puesto (IDEA.md §3).
CASOS = {"dona-lupe": {"lat": 19.3492, "lng": -99.1525}}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--caso", choices=sorted(CASOS), default="dona-lupe")
    p.add_argument("--url", help="API en marcha; sin esto escribe directo en data/live/altas.jsonl")
    args = p.parse_args()

    entrada = altas.AltaIn(
        ficha=altas.ficha_grabada(), origen="demo", confirmado=True, demo_data=True, **CASOS[args.caso]
    )
    if args.url:
        req = urllib.request.Request(
            f"{args.url.rstrip('/')}/api/altas",
            data=entrada.model_dump_json().encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            alta = json.loads(r.read())
    else:
        alta = altas.crear_alta(entrada).model_dump()
    print(f"ALTA {alta['id']} · h3 {alta['h3']} · página /n/{alta['slug']}")


if __name__ == "__main__":
    main()
