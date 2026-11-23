"""Builds one SVG of the real H3 grid (Coyoacán + Iztapalapa) with tianguis dots, for the design-lock mockups.
Classes: h1..h5 = quintile of actividad_tpv_est (simulado), ho = oculto; t = tianguis, m = mercado.
Usage: python3 hexsvg.py REPO_ROOT OUT_SVG"""
import json
import math
import sys

root, out = sys.argv[1], sys.argv[2]
g = json.load(open(f"{root}/data/processed/hex.geojson"))
pts = json.load(open(f"{root}/data/processed/tianguis_abierto.json"))
pts = [p for p in pts if p["alcaldia_cvegeo"] in ("09003", "09007")]

coords = [c for f in g["features"] for c in f["geometry"]["coordinates"][0]]
lng0, lng1 = min(c[0] for c in coords), max(c[0] for c in coords)
lat0, lat1 = min(c[1] for c in coords), max(c[1] for c in coords)
k = math.cos(math.radians((lat0 + lat1) / 2))
W = 1000
H = W * (lat1 - lat0) / ((lng1 - lng0) * k)


def xy(lng, lat):
    return (lng - lng0) / (lng1 - lng0) * W, (lat1 - lat) / (lat1 - lat0) * H


vals = sorted(f["properties"]["actividad_tpv_est"] or 0 for f in g["features"])
cuts = [vals[int(len(vals) * q)] for q in (0.2, 0.4, 0.6, 0.8)]

parts = []
for f in g["features"]:
    p = f["properties"]
    v = p["actividad_tpv_est"] or 0
    cls = "ho" if p["oculto"] else "h%d" % (1 + sum(v > c for c in cuts))
    d = "M" + "L".join("%.1f,%.1f" % xy(*c) for c in f["geometry"]["coordinates"][0]) + "Z"
    parts.append(f'<path class="{cls}" d="{d}"/>')
for p in pts:
    x, y = xy(p["lng"], p["lat"])
    parts.append(f'<circle class="{"t" if p["tipo"] == "tianguis" else "m"}" cx="{x:.1f}" cy="{y:.1f}" r="3.2"/>')

svg = (
    f'<svg class="mapa" viewBox="0 0 {W} {H:.0f}" role="img" '
    f'aria-label="Rejilla H3 de Coyoacán e Iztapalapa con {len(pts)} tianguis y mercados">' + "".join(parts) + "</svg>"
)
open(out, "w").write(svg)
print(len(g["features"]), "hex", len(pts), "points", f"{W}x{H:.0f}", len(svg) // 1024, "KB")
