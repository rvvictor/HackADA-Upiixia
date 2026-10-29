"""Apoyos de la demo: la historia simulada de la plataforma y el caso de Doña Lupe junto a la sede.

La historia (data/demo/plataforma_simulada.json) es SIMULADA y siempre viaja con demo_data: true.
"""

import json

from app import config

# Sede del evento (Utopía Elena Poniatowska Amor, San Lucas, Coyoacán): origen de la ruta de Karla en la demo.
SEDE = {"lat": 19.3486, "lng": -99.1530}
# El puesto de Doña Lupe para la demo: ~100 m de la sede, para que entre a la ruta de Karla (desvío máximo 5 min).
DONA_LUPE = {"lat": 19.3492, "lng": -99.1538}
LISTA_DEMO = "2 kilos de jitomate, tortillas, chiles secos, tenis para niño, pilas"


def historia() -> list[dict]:
    archivo = config.DEMO_DIR / "plataforma_simulada.json"
    if not archivo.exists():
        return []
    return json.loads(archivo.read_text(encoding="utf-8"))


def eventos_de(negocio_id: str) -> list[dict]:
    """Eventos simulados de un negocio, para su avance cuando todavía no tiene eventos reales."""
    return [e for e in historia() if e.get("negocio_id") == negocio_id]
