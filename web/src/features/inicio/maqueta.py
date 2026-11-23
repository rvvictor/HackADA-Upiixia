"""Coyoacán as an extruded hex model (oblique view) + tianguis markers by weekday, for design-lock direction C.
Also writes a flat SVG of both alcaldías for A and B. Real H3 grid; heights/colors come from simulado/estimado fields.
Usage: python3 maqueta.py REPO_ROOT OUT_DIR"""
import json
import math
import sys

root, out = sys.argv[1], sys.argv[2]
g = json.load(open(f"{root}/data/processed/hex.geojson"))
pts = json.load(open(f"{root}/data/processed/tianguis_abierto.json"))


def frame(features, W):
    cs = [c for f in features for c in f["geometry"]["coordinates"][0]]
    lng0, lng1 = min(c[0] for c in cs), max(c[0] for c in cs)
    lat0, lat1 = min(c[1] for c in cs), max(c[1] for c in cs)
    k = math.cos(math.radians((lat0 + lat1) / 2))
    H = W * (lat1 - lat0) / ((lng1 - lng0) * k)
    return (lambda lng, lat: ((lng - lng0) / (lng1 - lng0) * W, (lat1 - lat) / (lat1 - lat0) * H)), H


def quint(vals):
    s = sorted(vals)
    return [s[int(len(s) * q)] for q in (0.2, 0.4, 0.6, 0.8)]


# ---- C: Coyoacán model ----
coy = [f for f in g["features"] if f["properties"]["alcaldia_cvegeo"] == "09003"]
W = 1000
xy, H = frame(coy, W)
SQ = 0.58  # vertical squash = camera pitch
act = quint([f["properties"]["actividad_tpv_est"] or 0 for f in coy])
imp = quint([f["properties"]["impulso"] or 0 for f in coy])
ALT = [6, 14, 26, 42, 64]
tops = {}
suelo = {}  # CO-047: ground center of each block, to place tianguis that have no block of their own
cols = []
for f in coy:
    p = f["properties"]
    a = 0 if p["oculto"] else sum((p["actividad_tpv_est"] or 0) > c for c in act)
    i = sum((p["impulso"] or 0) > c for c in imp)
    h = 0 if p["oculto"] else ALT[a]
    ring = [xy(*c) for c in f["geometry"]["coordinates"][0]][:-1]
    ring = [(x, y * SQ) for x, y in ring]
    cy = sum(y for _, y in ring) / len(ring)
    cols.append((cy, ring, h, i + 1, p["oculto"]))
    tops[p["h3"]] = (sum(x for x, _ in ring) / len(ring), cy - h)
    suelo[p["h3"]] = (sum(x for x, _ in ring) / len(ring), cy)
cols.sort(key=lambda c: c[0])
parts = []
for cy, ring, h, ci, oc in cols:
    if oc:
        parts.append('<path class="z0" d="M' + "L".join(f"{x:.1f},{y:.1f}" for x, y in ring) + 'Z"/>')
        continue
    n = len(ring)
    for j in range(n):
        (x1, y1), (x2, y2) = ring[j], ring[(j + 1) % n]
        # visible side: the edge's outward normal points down-screen (toward the viewer)
        cx = sum(x for x, _ in ring) / n
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        if my <= cy + 0.01:
            continue
        side = "sl" if mx < cx else "sr"
        parts.append(
            f'<path class="{side} s{ci}" d="M{x1:.1f},{y1:.1f}L{x2:.1f},{y2:.1f}L{x2:.1f},{y2 - h:.1f}L{x1:.1f},{y1 - h:.1f}Z"/>'
        )
    parts.append(f'<path class="c{ci}" d="M' + "L".join(f"{x:.1f},{y - h:.1f}" for x, y in ring) + 'Z"/>')
marks = []
for p in pts:
    if p["alcaldia_cvegeo"] != "09003" or p["tipo"] != "tianguis":
        continue
    if p["h3"] in tops:
        x, y = tops[p["h3"]]
    else:
        # CO-047: no block for its hexagon. Stand on the nearest block; skip it if that is farther than ~1.5 blocks.
        gx, gy = xy(p["lng"], p["lat"])
        gy *= SQ
        d, k = min(((sx - gx) ** 2 + (sy - gy) ** 2, k) for k, (sx, sy) in suelo.items())
        if d > 34 ** 2:
            continue
        x, y = tops[k]
    dias = " ".join(f"d{d}" for d in p.get("dias") or [])
    marks.append(f'<g class="tg {dias}"><line x1="{x:.1f}" y1="{y:.1f}" x2="{x:.1f}" y2="{y - 18:.1f}"/><circle cx="{x:.1f}" cy="{y - 20:.1f}" r="4.2"/></g>')
Hc = H * SQ + 30
svg = (
    f'<svg class="maqueta" viewBox="0 -70 {W} {Hc + 70:.0f}" role="img" aria-label="Maqueta de Coyoacán: {len(coy)} hexágonos H3">'
    + "".join(parts) + "".join(marks) + "</svg>"
)
open(f"{out}/maqueta.svg", "w").write(svg)
print("C", len(coy), "hex", len(marks), "tianguis", len(svg) // 1024, "KB")
