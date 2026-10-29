"""Descarga única del DENUE (INEGI) por radio desde el centro de cada colonia, y filtro a negocios de barrio.

Uso: uv run python -m pipeline.denue [--cache RUTA]
El token sale de app.config.settings.denue_token; nunca se imprime ni se guarda (los errores se capturan sin la URL).
Llamadas secuenciales con pausa corta y tope de consultas.
"""

import argparse
import csv
import json
import sys
import time
from pathlib import Path

import httpx

from pipeline.negocios.filtros import clasificar

ROOT = Path(__file__).resolve().parents[2]
COLONIAS = ROOT / "data" / "raw" / "colonias_prioritarias.csv"
SALIDA = ROOT / "data" / "processed" / "negocios_denue.json"
BASE = "https://www.inegi.org.mx/app/api/denue/v1/consulta/Buscar"
FECHA = "2026-10-29"
COMPLETAS = {"3": "Coyoacán", "7": "Iztapalapa"}
MUESTRA_POR_ALCALDIA = 8  # colonias por alcaldía fuera de Coyoacán e Iztapalapa
RADIO_M = 700
PAUSA_S = 0.25
TOPE_CONSULTAS = 600
LIMITE_MINUTOS = 25

# Servicios de consumo cotidiano (por nombre de clase_actividad del DENUE; la API no devuelve la clave SCIAN).
SERVICIOS = (
    "Restaurantes", "Cafeterías", "Salones y clínicas de belleza", "Lavanderías", "Panificación tradicional",
    "Elaboración de tortillas", "Reparación y mantenimiento de otros artículos para el hogar", "Servicios de fotocopiado",
    "Cerrajerías", "Servicios veterinarios para mascotas", "Centros de acondicionamiento físico",
    "Servicios de acceso a computadoras", "Servicios de preparación de otros alimentos",
)
# Autoservicio y gran superficie: no son negocio de barrio (equivale a los giros excluidos de pipeline/negocios).
EXCLUIR_CLASE = ("minisupers", "supermercados", "tiendas departamentales", "autoservicio", "tiendas de descuento")


def es_giro_objetivo(clase: str) -> bool:
    c = clase.lower()
    if any(x in c for x in EXCLUIR_CLASE):
        return False
    return clase.startswith("Comercio al por menor") or clase.startswith("Farmacias") or clase.startswith(SERVICIOS)


def filtrar(crudos: list[dict], fecha: str = FECHA) -> list[dict]:
    """Registros crudos del DENUE -> negocios locales (giro de barrio, estrato chico, sin cadenas). Sin teléfonos ni correos."""
    vistos: dict[str, dict] = {}
    for r in crudos:
        if r.get("Id") and es_giro_objetivo(r.get("Clase_actividad", "")) and r.get("Latitud") and r.get("Longitud"):
            vistos[r["Id"]] = r
    candidatos = [
        {
            "nombre": r["Nombre"], "razon_social": r.get("Razon_social", ""), "clase_scian": "",
            "estrato": r.get("Estrato", ""), "_r": r,
        }
        for r in vistos.values()
    ]
    salida = []
    for n in clasificar(candidatos):
        if not n["es_barrial"]:
            continue
        r = n["_r"]
        salida.append({
            "id_denue": r["Id"], "nombre": r["Nombre"].strip(), "giro": r["Clase_actividad"].strip(),
            "colonia": r.get("Colonia", "").strip(), "lat": float(r["Latitud"]), "lng": float(r["Longitud"]),
            "tipo": "negocio_local", "tipo_dato": "real", "fuente": "DENUE INEGI", "fecha_consulta": fecha,
            "alcaldia": r.get("Ubicacion", "").split(",")[1].strip() if r.get("Ubicacion", "").count(",") >= 2 else "",
        })
    return sorted(salida, key=lambda x: x["id_denue"])


ALCALDIAS_CDMX = {
    "Álvaro Obregón", "Azcapotzalco", "Benito Juárez", "Coyoacán", "Cuajimalpa de Morelos", "Cuauhtémoc", "Gustavo A. Madero",
    "Iztacalco", "Iztapalapa", "La Magdalena Contreras", "Miguel Hidalgo", "Milpa Alta", "Tláhuac", "Tlalpan",
    "Venustiano Carranza", "Xochimilco",
}
TOPE_MUESTRA = 300  # negocios por alcaldía distinta de Coyoacán e Iztapalapa


def acotar(negocios: list[dict]) -> list[dict]:
    """Coyoacán e Iztapalapa completas; las demás alcaldías de la CDMX, una muestra repartida; se descarta lo que cae fuera de la CDMX."""
    por_alc: dict[str, list[dict]] = {}
    for n in negocios:
        if n["alcaldia"] in ALCALDIAS_CDMX:
            por_alc.setdefault(n["alcaldia"], []).append(n)
    salida = []
    for alc, lista in por_alc.items():
        if alc not in COMPLETAS.values() and len(lista) > TOPE_MUESTRA:
            lista = lista[:: len(lista) // TOPE_MUESTRA][:TOPE_MUESTRA]
        salida += lista
    return sorted(salida, key=lambda x: x["id_denue"])


def centros() -> list[tuple[str, float, float]]:
    """(cve_alcaldia, lat, lng) por colonia: 09003 y 09007 completas, el resto una muestra acotada y repartida."""
    por_alc: dict[str, list[tuple[float, float]]] = {}
    with COLONIAS.open(encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            lat, lng = (float(x) for x in fila["Geo Point"].split(","))
            por_alc.setdefault(fila["CVE_ALC"], []).append((lat, lng))
    salida = []
    for alc, pts in sorted(por_alc.items(), key=lambda kv: int(kv[0])):
        if alc not in COMPLETAS:
            paso = max(1, len(pts) // MUESTRA_POR_ALCALDIA)
            pts = pts[::paso][:MUESTRA_POR_ALCALDIA]
        salida += [(alc, lat, lng) for lat, lng in pts]
    return salida


def consultar(cliente: httpx.Client, token: str, lat: float, lng: float) -> list[dict]:
    try:
        r = cliente.get(f"{BASE}/todos/{lat},{lng}/{RADIO_M}/{token}")
        r.raise_for_status()
        datos = r.json()
        return datos if isinstance(datos, list) else []
    except Exception as e:  # sin e ni la URL: el mensaje de httpx puede incluir el token
        print(f"  consulta fallida ({type(e).__name__})", file=sys.stderr)
        return []


def descargar(token: str) -> tuple[list[dict], dict]:
    crudos: dict[str, dict] = {}
    consultas, inicio, completa = 0, time.monotonic(), True
    puntos = centros()
    with httpx.Client(timeout=90) as cliente:
        for i, (alc, lat, lng) in enumerate(puntos, 1):
            if consultas >= TOPE_CONSULTAS or time.monotonic() - inicio > LIMITE_MINUTOS * 60:
                completa = False
                break
            for r in consultar(cliente, token, lat, lng):
                crudos[r["Id"]] = r
            consultas += 1
            if i % 25 == 0:
                print(f"  {i}/{len(puntos)} consultas, {len(crudos)} crudos")
            time.sleep(PAUSA_S)
    return list(crudos.values()), {"consultas": consultas, "puntos": len(puntos), "completa": completa}


def main() -> None:
    from app.config import settings

    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", type=Path, help="JSON con crudos (fuera del repo); si existe se reusa y no hay red")
    args = ap.parse_args()
    if args.cache and args.cache.exists():
        crudos, meta = json.loads(args.cache.read_text(encoding="utf-8")), {}
    else:
        if not settings.denue_token:
            sys.exit("Falta DENUE_TOKEN en .env")
        crudos, meta = descargar(settings.denue_token)
        if args.cache:
            args.cache.write_text(json.dumps(crudos, ensure_ascii=False), encoding="utf-8")
    negocios = acotar(filtrar(crudos, FECHA))
    SALIDA.write_text(json.dumps(negocios, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"crudos={len(crudos)} negocios_locales={len(negocios)} {meta}")


if __name__ == "__main__":
    main()
