"""Genera data/processed/negocios.json: negocios SIMULADOS con la forma del DENUE para Coyoacán e Iztapalapa.

Uso: uv run python -m pipeline.negocios   (también escribe data/processed/programas.json)
Determinista (semilla fija). Todo registro lleva tipo_dato "simulado"; la regla anti-cadenas (filtros.py) es real.
"""

import json
import random
from datetime import date, timedelta
from pathlib import Path

import h3

from pipeline.negocios.clases import CLASES
from pipeline.negocios.filtros import clasificar
from pipeline.negocios.programas import PROGRAMAS

ROOT = Path(__file__).resolve().parents[2]
SALIDA = ROOT / "data" / "processed" / "negocios.json"
SALIDA_PROGRAMAS = ROOT / "data" / "processed" / "programas.json"
SEMILLA = 20261025
H3_RES = 9

# Sede del evento: Utopía Elena Poniatowska Amor, San Lucas, Coyoacán (aprox.). La demo de la ruta sale de aquí.
SEDE = (19.3486, -99.1530)

ALCALDIAS = {
    "09003": {
        "nombre": "Coyoacán",
        "caja": (19.295, 19.360, -99.195, -99.105),
        "colonias": ["San Lucas", "Del Carmen", "Santa Catarina", "Ajusco", "Pedregal de Santo Domingo",
                     "Culhuacán", "Santa Úrsula Coapa", "Copilco", "El Rosario", "Ciudad Jardín"],
        "n": 230,
    },
    "09007": {
        "nombre": "Iztapalapa",
        "caja": (19.300, 19.400, -99.095, -98.980),
        "colonias": ["San Lucas Iztapalapa", "Santa Martha Acatitla", "Desarrollo Urbano Quetzalcóatl",
                     "San Miguel Teotongo", "Ejército de Oriente", "Juan Escutia", "Los Reyes Culhuacán",
                     "Santa Cruz Meyehualco", "El Manto", "Barrio San Pablo"],
        "n": 240,
    },
}

# Peso de cada giro barrial en la muestra (cuántos salen de cada uno).
PESOS = {
    "461110": 18, "461130": 8, "311830": 7, "311812": 5, "461121": 4, "461122": 4, "461140": 3, "461150": 4,
    "461160": 2, "463211": 5, "463310": 4, "464111": 3, "465311": 4, "467111": 4, "466410": 3, "722514": 6,
    "722519": 5, "811430": 2, "812110": 5, "811211": 2,
}
PREFIJOS = {
    "461110": ["Abarrotes", "Miscelánea", "Tienda"], "461130": ["Recaudería", "Frutas y Verduras"],
    "311830": ["Tortillería", "Molino y Tortillería"], "311812": ["Panadería"], "461121": ["Carnicería"],
    "461122": ["Pollería"], "461140": ["Chiles y Semillas", "Especias"], "461150": ["Cremería"],
    "461160": ["Dulcería"], "463211": ["Ropa", "Boutique"], "463310": ["Zapatería", "Calzado"],
    "464111": ["Farmacia"], "465311": ["Papelería"], "467111": ["Ferretería", "Tlapalería"],
    "466410": ["Celulares"], "722514": ["Tacos", "Taquería"], "722519": ["Fonda", "Cocina Económica"],
    "811430": ["Reparación de Calzado"], "812110": ["Estética"], "811211": ["Reparación de Celulares"],
}
NOMBRES = ["Doña Mary", "La Esperanza", "El Güero", "Los Arcos", "La Guadalupana", "San Judas", "El Buen Precio",
           "Don Chucho", "La Morena", "Los Compadres", "La Paloma", "El Rincón", "Doña Toña", "La Bendición",
           "El Pípila", "Las Flores", "Lupita", "El Chino", "La Escondida", "Los Gemelos", "Doña Rosa",
           "El Paisa", "San Martín", "Los Primos", "La Favorita", "El Sabor", "Doña Chela",
           "El Molino", "La Huerta", "Los Ángeles", "La Joya", "Don Beto", "La Estrella"]

CADENAS = [  # (nombre, razón social, clase, estrato), con presencia repetida como en el DENUE real
    ("OXXO", "CADENA COMERCIAL OXXO SA DE CV", "462112", "6 a 10 personas"),
    ("BODEGA AURRERA EXPRESS", "NUEVA WAL MART DE MEXICO S DE RL DE CV", "462111", "11 a 30 personas"),
    ("FARMACIAS SIMILARES", "FARMACIAS DE SIMILARES SA DE CV", "464111", "0 a 5 personas"),
    ("7-ELEVEN", "7-ELEVEN MEXICO SA DE CV", "462112", "6 a 10 personas"),
    ("COPPEL", "COPPEL SA DE CV", "462210", "31 a 50 personas"),
    ("TIENDAS NETO", "TIENDAS NETO SA DE CV", "462111", "6 a 10 personas"),
    ("TELCEL", "RADIOMOVIL DIPSA SA DE CV", "466410", "0 a 5 personas"),
    ("TACOS DON MANOLITO", "OPERADORA DE TACOS DM SA DE CV", "722514", "6 a 10 personas"),
]
FORMAS_PAGO = ["efectivo", "transferencia", "dimo", "codi", "tarjeta"]


def punto(rng: random.Random, cvegeo: str) -> tuple[float, float]:
    # 35% cerca de la sede para que la ruta de la demo tenga de dónde elegir; el resto en toda la alcaldía.
    if cvegeo == "09003" and rng.random() < 0.35:
        return SEDE[0] + rng.gauss(0, 0.006), SEDE[1] + rng.gauss(0, 0.006)
    lat0, lat1, lng0, lng1 = ALCALDIAS[cvegeo]["caja"]
    return rng.uniform(lat0, lat1), rng.uniform(lng0, lng1)


def generar() -> list[dict]:
    rng = random.Random(SEMILLA)
    negocios: list[dict] = []
    usados: set[str] = set()
    clases = list(PESOS)
    pesos = [PESOS[c] for c in clases]

    def agregar(cvegeo: str, nombre: str, razon: str, clase: str, estrato: str, lat: float, lng: float) -> None:
        i = len(negocios) + 1
        negocios.append({
            "id": f"neg-{i:04d}",
            "clee": f"SIM{cvegeo}{i:06d}",
            "nombre": nombre,
            "razon_social": razon,
            "clase_scian": clase,
            "clase_nombre": CLASES[clase],
            "estrato": estrato,
            "tipo_establecimiento": "Semifijo" if clase in {"461130", "722514"} and rng.random() < 0.3 else "Fijo",
            "lat": round(lat, 6),
            "lng": round(lng, 6),
            "h3": h3.latlng_to_cell(lat, lng, H3_RES),
            "alcaldia_cvegeo": cvegeo,
            "colonia": rng.choice(ALCALDIAS[cvegeo]["colonias"]),
            "fecha_alta_denue": (date(2010, 1, 1) + timedelta(days=rng.randrange(0, 5700))).isoformat(),
            "formas_pago": ["efectivo"] + rng.sample(FORMAS_PAGO[1:], rng.randint(0, 2)),
            "acepta_mercomuna": rng.random() < 0.3,
            "es_barrial": True,
            "motivo_exclusion": None,
            "tipo_dato": "simulado",
        })

    for cvegeo, alc in ALCALDIAS.items():
        for _ in range(alc["n"]):
            clase = rng.choices(clases, pesos)[0]
            for _intento in range(20):
                nombre = f"{rng.choice(PREFIJOS[clase])} {rng.choice(NOMBRES)}"
                if nombre not in usados:
                    break
                nombre = f"{nombre} {rng.randint(2, 99)}"
                if nombre not in usados:
                    break
            usados.add(nombre)
            estrato = "0 a 5 personas" if rng.random() < 0.85 else "6 a 10 personas"
            agregar(cvegeo, nombre, "", clase, estrato, *punto(rng, cvegeo))
        for nombre, razon, clase, estrato in CADENAS:
            for _ in range(3):
                agregar(cvegeo, nombre, razon, clase, estrato, *punto(rng, cvegeo))

    # Un par de negocios medianos que no son cadena pero no pasan el filtro de tamaño.
    agregar("09003", "Mueblería Hermanos Pérez", "", "463211", "11 a 30 personas", SEDE[0] + 0.004, SEDE[1] - 0.003)
    agregar("09007", "Materiales La Viga", "", "467111", "31 a 50 personas", 19.355, -99.06)
    return clasificar(negocios)


def main() -> None:
    negocios = generar()
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(json.dumps(negocios, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    barriales = sum(n["es_barrial"] for n in negocios)
    SALIDA_PROGRAMAS.write_text(json.dumps(PROGRAMAS, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"negocios.json: {len(negocios)} negocios, {barriales} barriales, {len(negocios) - barriales} excluidos")


if __name__ == "__main__":
    main()
