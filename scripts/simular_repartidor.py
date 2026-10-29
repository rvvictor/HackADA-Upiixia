"""Plan B de la demo: da de alta un repartidor y publica ofertas de ruta, sin Telegram ni internet.

    uv run python scripts/simular_repartidor.py --url http://127.0.0.1:8000        # API en marcha (DEMO_MODE=1)
    uv run python scripts/simular_repartidor.py --url http://127.0.0.1:8000 --ofertas 5 --cada 8

El alta, el código y la sesión van por la API real (`POST /api/repartidores`, `/codigo`, `/sesion`).
La API no expone un endpoint para crear ofertas (las publica el negocio/SEDECO en producción), así que
se siembran con `app.services.ofertas.crear` en data/live/ofertas.jsonl, el mismo archivo que lee la API.
Todo con `demo_data: true`. Con `--cada S` publica una oferta cada S segundos: el portal #/repartidor
la muestra sin recargar.
"""

import argparse
import json
import math
import sys
import time
import urllib.request
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from app.services import ofertas  # noqa: E402

ALCALDIAS = {"coyoacan": "09003", "iztapalapa": "09007"}
# Respaldo si data/processed/negocios.json no existe (Coyoacán, alrededor de SEDE).
NEGOCIOS_DEMO = [
    {"id": "N-DEMO", "nombre": "Fonda Doña Lupe", "clase_nombre": "fonda", "colonia": "San Lucas", "lat": 19.3468, "lng": -99.1617},
    {"id": "N-DEMO2", "nombre": "Panadería La Espiga", "clase_nombre": "panaderia", "colonia": "San Lucas", "lat": 19.3471, "lng": -99.1620},
    {"id": "N-DEMO3", "nombre": "Tortillería El Barrio", "clase_nombre": "tortilleria", "colonia": "San Lucas", "lat": 19.3490, "lng": -99.1590},
]


def negocios(cvegeo: str) -> list[dict]:
    for ruta in (RAIZ / "data/processed/negocios.json", RAIZ / "data/demo/negocios.json"):
        if ruta.is_file():
            try:
                filas = [n for n in json.loads(ruta.read_text(encoding="utf-8"))
                         if n.get("alcaldia_cvegeo") == cvegeo and n.get("colonia") and n.get("es_barrial", True)]
            except (ValueError, TypeError):
                continue
            if filas:
                return filas
    return NEGOCIOS_DEMO


def _dist_m(a: dict, b: dict) -> int:
    dy = (a["lat"] - b["lat"]) * 111_000
    dx = (a["lng"] - b["lng"]) * 111_000 * math.cos(math.radians(a["lat"]))
    return int(math.hypot(dx, dy))


def sembrar_ofertas(n: int, colonias: list[str], pool: list[dict], ahora: float | None = None, desde: int = 0) -> list[dict]:
    """Crea `n` ofertas demo: cada una va de un negocio a una parada cercana de la misma colonia."""
    por_colonia = [x for x in pool if x.get("colonia") in colonias] or pool
    creadas = []
    for i in range(desde, desde + n):
        origen = por_colonia[(i * 7) % len(por_colonia)]
        destino = por_colonia[(i * 7 + 3 + i // 3) % len(por_colonia)]
        dist = max(250, _dist_m(origen, destino)) if destino is not origen else 400
        dist = min(dist, 2500)
        minutos = max(5, round(dist / 80))
        creadas.append(ofertas.crear({
            "negocio_id": origen.get("id", "N-DEMO"),
            "tipo_negocio": str(origen.get("clase_nombre") or "negocio").lower(),
            "colonia": origen["colonia"],
            "paradas": [{"lat": origen["lat"], "lng": origen["lng"], "colonia": origen["colonia"]},
                        {"lat": destino["lat"], "lng": destino["lng"], "colonia": destino.get("colonia", origen["colonia"])}],
            "distancia_m": dist, "minutos_est": minutos, "pago_est": 20 + minutos * 3,
            "tipo_dato_pago": "simulado", "demo_data": True,
        }, ahora=ahora))
    return creadas


def _post(url: str, ruta: str, cuerpo: dict) -> dict:
    req = urllib.request.Request(f"{url.rstrip('/')}{ruta}", data=json.dumps(cuerpo).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--url", default="http://127.0.0.1:8000", help="API en marcha (con DEMO_MODE=1 devuelve el código)")
    p.add_argument("--alcaldia", choices=sorted(ALCALDIAS), default="coyoacan")
    p.add_argument("--nombre", default="Rafa (demo)")
    p.add_argument("--ofertas", type=int, default=3, help="cuántas ofertas publicar")
    p.add_argument("--cada", type=float, default=0, help="segundos entre ofertas (para verlas llegar sin recargar)")
    args = p.parse_args()

    cvegeo = ALCALDIAS[args.alcaldia]
    pool = negocios(cvegeo)
    colonias = [c for c, _ in Counter(n["colonia"] for n in pool).most_common(3)]
    # Estudiante de 19 años: prioridad máxima, ve las ofertas primero (la prioridad nunca sale en la API).
    rep = _post(args.url, "/api/repartidores", {
        "nombre_mostrar": args.nombre, "edad": 19, "estudiante": True, "alcaldia_cvegeo": cvegeo,
        "colonias": colonias, "transporte": "bici", "demo_data": True})
    rid = rep["id"]
    cod = _post(args.url, "/api/repartidores/codigo", {"id": rid})
    codigo = cod.get("codigo")
    if not codigo:
        sys.exit("La API no devolvió el código: arráncala con DEMO_MODE=1 (en producción llega por Telegram).")
    _post(args.url, "/api/repartidores/sesion", {"id": rid, "codigo": codigo})  # comprueba que el acceso funciona
    # Código de un solo uso: se pide otro para que la persona de la demo entre por la UI.
    codigo = _post(args.url, "/api/repartidores/codigo", {"id": rid})["codigo"]

    print(f"REPARTIDOR {rid} · código {codigo} · colonias {', '.join(colonias)}")
    print(f"Portal: {args.url.rstrip('/')}/#/repartidor  (entra con {rid} y {codigo}; el código vence en 10 min)")
    for i in range(args.ofertas):
        if i and args.cada:
            time.sleep(args.cada)
        o = sembrar_ofertas(1, colonias, pool, desde=i * 5 + len(ofertas._todas()))[0]
        print(f"OFERTA {o['id']} · {o['tipo_negocio']} en {o['colonia']} · {o['distancia_m']} m · ${o['pago_est']} (simulado)", flush=True)


if __name__ == "__main__":
    main()
