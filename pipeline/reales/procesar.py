"""Convierte `data/raw/` en JSON de `data/processed/` con tipo_dato real.

Uso: `uv run python -m pipeline.reales [--raw data/raw] [--salida data/processed]`
Las funciones reciben rutas, así las pruebas usan mini-muestras sin depender de `data/raw/`.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import unicodedata
from pathlib import Path

import h3

FECHA = "2026-10-25"
RES_H3 = 9
PRIORIDAD = {"09003", "09007"}  # Coyoacán e Iztapalapa

# Claves INEGI de las 16 alcaldías, por nombre normalizado.
ALCALDIAS = {
    "AZCAPOTZALCO": "09002", "COYOACAN": "09003", "CUAJIMALPA DE MORELOS": "09004",
    "GUSTAVO A MADERO": "09005", "IZTACALCO": "09006", "IZTAPALAPA": "09007",
    "LA MAGDALENA CONTRERAS": "09008", "MILPA ALTA": "09009", "ALVARO OBREGON": "09010",
    "TLAHUAC": "09011", "TLALPAN": "09012", "XOCHIMILCO": "09013", "BENITO JUAREZ": "09014",
    "CUAUHTEMOC": "09015", "MIGUEL HIDALGO": "09016", "VENUSTIANO CARRANZA": "09017",
}
NOMBRES = {
    "09002": "Azcapotzalco", "09003": "Coyoacán", "09004": "Cuajimalpa de Morelos",
    "09005": "Gustavo A. Madero", "09006": "Iztacalco", "09007": "Iztapalapa",
    "09008": "La Magdalena Contreras", "09009": "Milpa Alta", "09010": "Álvaro Obregón",
    "09011": "Tláhuac", "09012": "Tlalpan", "09013": "Xochimilco", "09014": "Benito Juárez",
    "09015": "Cuauhtémoc", "09016": "Miguel Hidalgo", "09017": "Venustiano Carranza",
}
DIAS = {"LUNES": 0, "MARTES": 1, "MIERCOLES": 2, "JUEVES": 3, "VIERNES": 4, "SABADO": 5, "DOMINGO": 6}


def arreglar_acentos(texto: str) -> str:
    """Repara mojibake (UTF-8 leído como cp1252/latin-1: `BRASILEÃ‘OS` -> `BRASILEÑOS`).
    Si no hay patrón de mojibake, devuelve el texto igual."""
    if "Ã" not in texto and "Â" not in texto:
        return texto
    for cod in ("cp1252", "latin-1"):
        try:
            return texto.encode(cod).decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            continue
    return texto


def norm(texto: str | None) -> str:
    """Clave de cruce: sin acentos, mayúsculas, sin puntuación, espacios simples."""
    t = unicodedata.normalize("NFKD", arreglar_acentos(texto or ""))
    t = "".join(c for c in t if not unicodedata.combining(c)).upper()
    t = re.sub(r"[^A-Z0-9 ]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def cve_alcaldia(nombre: str | None) -> str | None:
    return ALCALDIAS.get(norm(nombre))


def titulo(texto: str) -> str:
    return arreglar_acentos(texto).strip()


def parsear_dias(texto: str) -> list[int]:
    n = norm(texto)
    return sorted({v for k, v in DIAS.items() if k in n})


def parsear_horario(texto: str) -> tuple[str, str] | None:
    m = re.search(r"(\d{1,2}):(\d{2})\s*A\s*(\d{1,2}):(\d{2})", texto.upper())
    if not m:
        return None
    a, b, c, d = m.groups()
    return f"{int(a):02d}:{b}", f"{int(c):02d}:{d}"


def _num(v: str | None) -> float | None:
    try:
        return float(v) if v not in (None, "", "NA") else None
    except ValueError:
        return None


def _limpio(v: str | None) -> str | None:
    v = (v or "").strip()
    return None if v in ("", "NA", "0") else titulo(v)


def leer_csv(ruta: Path) -> list[dict]:
    with open(ruta, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _base(fuente: str) -> dict:
    return {"tipo_dato": "real", "fuente": fuente, "fecha_consulta": FECHA}


def procesar_tianguis(ruta: Path) -> tuple[list[dict], dict]:
    fuente = f"data/raw/{ruta.name} (datos abiertos CDMX; sitio exacto por confirmar)"
    filas, sin_alc, sin_coord, sin_hor = [], 0, 0, 0
    contador: dict[str, int] = {}
    for r in leer_csv(ruta):
        cve = cve_alcaldia(r.get("alcaldia"))
        lat, lng = _num(r.get("latitud")), _num(r.get("longitud"))
        if not cve:
            sin_alc += 1
            continue
        if lat is None or lng is None:
            sin_coord += 1
            continue
        hor = parsear_horario(r.get("horario", ""))
        if not hor:
            sin_hor += 1
            hor = ("08:00", "17:00")
        contador[cve] = contador.get(cve, 0) + 1
        colonia = titulo(r.get("colonia", "")) or None
        giro = _limpio(r.get("giro"))
        filas.append({
            "id": f"real-t-{cve}-{contador[cve]:04d}",
            "tipo": "tianguis",
            "nombre": f"Tianguis {colonia}" if colonia else "Tianguis",
            "alcaldia_cvegeo": cve,
            "colonia": colonia,
            "lat": lat, "lng": lng,
            "h3": h3.latlng_to_cell(lat, lng, RES_H3),
            "dias": parsear_dias(r.get("dia", "")),
            "abre": hor[0], "cierra": hor[1],
            "giros": [giro] if giro else [],
            "productos": [], "formas_pago": [],
            "acepta_mercomuna": None,
            "ubicacion": titulo(r.get("ubicacion", "")) or None,
            "fecha_verificacion": None, "verificado_por": None,
            **_base(fuente),
        })
    return filas, {"sin_alcaldia": sin_alc, "sin_coordenadas": sin_coord, "horario_por_defecto": sin_hor}


def procesar_mercados(ruta: Path) -> tuple[list[dict], dict]:
    fuente = f"data/raw/{ruta.name} (mercados públicos CDMX; sitio exacto por confirmar)"
    filas, descartes, contador = [], 0, {}
    for r in leer_csv(ruta):
        cve = cve_alcaldia(r.get("alcaldia_mercado"))
        lat, lng = _num(r.get("latitud")), _num(r.get("longitud"))
        if not cve or lat is None or lng is None:
            descartes += 1
            continue
        contador[cve] = contador.get(cve, 0) + 1
        nombre = titulo(r.get("mercado", ""))
        filas.append({
            "id": f"real-m-{cve}-{contador[cve]:04d}",
            "tipo": "mercado",
            "nombre": f"Mercado {nombre}",
            "numero": int(_num(r.get("numero"))) if _num(r.get("numero")) is not None else None,
            "alcaldia_cvegeo": cve,
            "colonia": _limpio(r.get("colonia_mercado")),
            "direccion": _limpio(r.get("direccion")),
            "lat": lat, "lng": lng,
            "h3": h3.latlng_to_cell(lat, lng, RES_H3),
            "locales": int(_num(r.get("locales"))) if _num(r.get("locales")) is not None else None,
            "superficie_m2": _num(r.get("superficie_m2")),
            "anio_inauguracion": (r.get("anio_inauguracion") or "")[:4] or None,
            "tipo_mercado": _limpio(r.get("tipo")),
            # La fuente no trae horario: valores por defecto para cumplir el esquema.
            "dias": [0, 1, 2, 3, 4, 5, 6], "abre": "07:00", "cierra": "18:00",
            "horario_por_defecto": True,
            "giros": [g] if (g := _limpio(r.get("giro"))) else [],
            "productos": [], "formas_pago": [], "acepta_mercomuna": None,
            "fecha_verificacion": None, "verificado_por": None,
            **_base(fuente),
        })
    return filas, {"descartados": descartes}


def centroide(geom: dict) -> tuple[float, float] | None:
    """Centroide (lat, lng) del anillo exterior más grande, por fórmula del polígono (shoelace)."""
    if geom["type"] == "Polygon":
        anillos = [geom["coordinates"][0]]
    elif geom["type"] == "MultiPolygon":
        anillos = [p[0] for p in geom["coordinates"]]
    else:
        return None
    mejor, area_mejor = None, -1.0
    for a in anillos:
        s = cx = cy = 0.0
        for (x0, y0), (x1, y1) in zip(a, a[1:] + a[:1]):
            c = x0 * y1 - x1 * y0
            s += c
            cx += (x0 + x1) * c
            cy += (y0 + y1) * c
        if abs(s) > area_mejor and s != 0:
            area_mejor = abs(s)
            mejor = (cy / (3 * s), cx / (3 * s))
    if mejor is None and anillos and anillos[0]:
        xs, ys = [p[0] for p in anillos[0]], [p[1] for p in anillos[0]]
        mejor = (sum(ys) / len(ys), sum(xs) / len(xs))
    return (round(mejor[0], 6), round(mejor[1], 6)) if mejor else None


def procesar_marginacion(ruta: Path) -> tuple[list[dict], dict]:
    fuente = f"data/raw/indice_marginacion/{ruta.name} (CONAPO, índice de marginación por colonia 2020)"
    filas = []
    for f in json.loads(ruta.read_text(encoding="utf-8"))["features"]:
        p = f["properties"]
        cve = p.get("CVE_MUN") or cve_alcaldia(p.get("NOM_MUN"))
        c = centroide(f["geometry"]) if f.get("geometry") else None
        filas.append({
            "alcaldia_cvegeo": cve,
            "colonia": titulo(p.get("COLONIA") or ""),
            "cp": p.get("CP"),
            "im_2020": p.get("IM_2020"), "gm_2020": p.get("GM_2020"), "imn_2020": p.get("IMN_2020"),
            "lat": c[0] if c else None, "lng": c[1] if c else None,
            **_base(fuente),
        })
    return filas, {}


def procesar_contaminacion(ruta: Path) -> tuple[list[dict], dict]:
    fuente = f"data/raw/{ruta.name} (nivel de contaminación promedio por colonia; año y método por confirmar)"
    filas = []
    for r in leer_csv(ruta):
        cve = cve_alcaldia(r.get("Alcaldia")) or (f"09{r['CVE_ALC'].zfill(3)}" if r.get("CVE_ALC") else None)
        punto = (r.get("Geo Point") or "").split(",")
        lat = _num(punto[0]) if len(punto) == 2 else None
        lng = _num(punto[1]) if len(punto) == 2 else None
        filas.append({
            "alcaldia_cvegeo": cve,
            "colonia": titulo(r.get("nombre_colonia", "")),
            "clave_colonia": r.get("clave_colonia"),
            "nivel_contaminacion": (r.get("nivel_contaminacion") or "").strip().lower() or None,
            "lat": lat, "lng": lng,
            **_base(fuente),
        })
    return filas, {}


def procesar_colonias(ruta: Path, marginacion: list[dict], contaminacion: list[dict]) -> tuple[list[dict], dict]:
    """Una fila por colonia con centroide (sin polígono: pesa ~33 MB y el mapa no lo necesita)."""
    fuente = f"data/raw/{ruta.name} (catálogo de colonias CDMX; sitio exacto por confirmar)"
    ind_m = {(m["alcaldia_cvegeo"], norm(m["colonia"])): m for m in marginacion}
    ind_c = {(c["alcaldia_cvegeo"], norm(c["colonia"])): c for c in contaminacion}
    filas, con_m, con_c = [], 0, 0
    for f in json.loads(ruta.read_text(encoding="utf-8"))["features"]:
        p = f["properties"]
        cve = f"09{p['cve_alc'].zfill(3)}" if p.get("cve_alc") else cve_alcaldia(p.get("alc"))
        clave = (cve, norm(p.get("colonia")))
        m, c = ind_m.get(clave), ind_c.get(clave)
        con_m += m is not None
        con_c += c is not None
        cen = centroide(f["geometry"]) if f.get("geometry") else None
        filas.append({
            "id": p.get("cve_col"),
            "colonia": titulo(p.get("colonia") or ""),
            "alcaldia_cvegeo": cve,
            "alcaldia": NOMBRES.get(cve, p.get("alc")),
            "clasif": p.get("clasif"),
            "lat": cen[0] if cen else None, "lng": cen[1] if cen else None,
            "prioridad": cve in PRIORIDAD,
            "marginacion_gm": m["gm_2020"] if m else None,
            "marginacion_im": m["im_2020"] if m else None,
            "nivel_contaminacion": c["nivel_contaminacion"] if c else None,
            **_base(fuente),
        })
    return filas, {"con_marginacion": con_m, "con_contaminacion": con_c, "total": len(filas)}


def cruzar_indices(colonias: list[dict], filas: list[dict]) -> int:
    """Marca en cada fila de un índice si cruzó con una colonia del catálogo; devuelve cuántas cruzaron."""
    claves = {(c["alcaldia_cvegeo"], norm(c["colonia"])): c["id"] for c in colonias}
    n = 0
    for f in filas:
        cid = claves.get((f["alcaldia_cvegeo"], norm(f["colonia"])))
        f["colonia_id"] = cid
        n += cid is not None
    return n


def escribir(ruta: Path, datos) -> None:
    ruta.write_text(json.dumps(datos, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def ejecutar(raw: Path, salida: Path) -> dict:
    tian, e1 = procesar_tianguis(raw / "ubicacion_tianguis.csv")
    merc, e2 = procesar_mercados(raw / "diccionario_tianguis.csv")
    marg, _ = procesar_marginacion(raw / "indice_marginacion" / "marginacion.json")
    cont, _ = procesar_contaminacion(raw / "colonias_prioritarias.csv")
    col, e3 = procesar_colonias(raw / "diccionario_colonias.json", marg, cont)
    e3["marginacion_cruzada"] = cruzar_indices(col, marg)
    e3["contaminacion_cruzada"] = cruzar_indices(col, cont)
    e3["marginacion_total"], e3["contaminacion_total"] = len(marg), len(cont)
    salida.mkdir(parents=True, exist_ok=True)
    escribir(salida / "tianguis_abierto.json", tian + merc)
    escribir(salida / "mercados.json", merc)
    escribir(salida / "colonias.json", col)
    escribir(salida / "marginacion_colonia.json", marg)
    escribir(salida / "contaminacion_colonia.json", cont)
    return {"tianguis": len(tian), "mercados": len(merc), "colonias": len(col), **e1, **e2, **e3}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--raw", type=Path, default=Path("data/raw"))
    ap.add_argument("--salida", type=Path, default=Path("data/processed"))
    a = ap.parse_args()
    print(json.dumps(ejecutar(a.raw, a.salida), ensure_ascii=False, indent=1))
