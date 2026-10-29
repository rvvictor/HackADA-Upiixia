"""Negocio: ficha, avance de 7 días, escalera de barrio y programas.

Lee `negocios.json` (directorio DENUE), `altas.jsonl` (altas de la plataforma), `programas.json`
y `eventos.jsonl`. Las ediciones de ficha se guardan en `LIVE_DIR/fichas/{id}.json`.
Nunca muestra ventas ni ingresos: la ficha tiene una lista blanca de campos.
"""

import hashlib
import json
import random
import re
from collections import Counter
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from app import config

VENTANA_DIAS = 7
ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")
FICHA_CAMPOS = (
    "nombre",
    "giro",
    "colonia",
    "telefono",
    "horario",
    "formas_pago",
    "productos",
    "acepta_mercomuna",
    "ubicacion",
    "aparecer_en_rutas",
)
# Tipo de evento -> clave en el avance.
AVANCE_CLAVES = {
    "busqueda": "busquedas",
    "aparicion_ruta": "rutas",
    "compre_aqui": "compre_aqui",
    "vista_pagina": "visitas_pagina",
}


def valid_id(negocio_id: str) -> bool:
    return bool(ID_RE.match(negocio_id or ""))


def _leer_json(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def _leer_jsonl(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    filas = []
    for linea in path.read_text(encoding="utf-8").splitlines():
        if not linea.strip():
            continue
        try:
            fila = json.loads(linea)
        except json.JSONDecodeError:
            continue
        if isinstance(fila, dict):
            filas.append(fila)
    return filas


def _parse_ts(texto: Any) -> datetime | None:
    # eventos.jsonl (PB-007) guarda ts como epoch; las filas antiguas como ISO.
    if isinstance(texto, (int, float)) and not isinstance(texto, bool):
        return datetime.fromtimestamp(texto, UTC)
    if not isinstance(texto, str):
        return None
    try:
        ts = datetime.fromisoformat(texto)
    except ValueError:
        return None
    return ts if ts.tzinfo else ts.replace(tzinfo=UTC)


DIAS_NOMBRE = ("lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo")


def horario_desde_ficha(dias: Any, abre: Any, cierra: Any) -> str | None:
    """Texto de horario a partir de la ficha del bot: días 0 = lunes … 6 = domingo.

    [0, 1, 2, 3, 4], "07:00", "15:00" -> "lunes a viernes de 07:00 a 15:00".
    """
    if not abre or not cierra:
        return None
    hora = f"{abre} a {cierra}"
    ok = sorted({d for d in (dias if isinstance(dias, list) else []) if isinstance(d, int) and 0 <= d <= 6})
    if not ok:
        return hora
    tramos: list[tuple[int, int]] = []
    ini = prev = ok[0]
    for d in ok[1:] + [None]:
        if d is not None and d == prev + 1:
            prev = d
            continue
        tramos.append((ini, prev))
        if d is not None:
            ini = prev = d
    partes = [DIAS_NOMBRE[a] if a == b else f"{DIAS_NOMBRE[a]} a {DIAS_NOMBRE[b]}" for a, b in tramos]
    texto = partes[0] if len(partes) == 1 else ", ".join(partes[:-1]) + " y " + partes[-1]
    return f"{texto} de {hora}"


def _base_directorio() -> dict[str, dict]:
    filas = _leer_json(config.PROCESSED_DIR / "negocios.json", [])
    base: dict[str, dict] = {}
    for fila in filas if isinstance(filas, list) else []:
        if not isinstance(fila, dict) or not fila.get("id"):
            continue
        base[str(fila["id"])] = {
            "id": str(fila["id"]),
            "origen": "directorio",
            "nombre": fila.get("nombre"),
            "giro": fila.get("clase_nombre"),
            "colonia": fila.get("colonia"),
            "formas_pago": fila.get("formas_pago") or [],
            "acepta_mercomuna": bool(fila.get("acepta_mercomuna")),
            "h3": fila.get("h3"),
            "lat": fila.get("lat"),
            "lng": fila.get("lng"),
        }
    return base


def _altas() -> dict[str, dict]:
    altas: dict[str, dict] = {}
    for fila in _leer_jsonl(config.LIVE_DIR / "altas.jsonl"):
        if not fila.get("id"):
            continue
        ficha = fila.get("ficha") if isinstance(fila.get("ficha"), dict) else {}
        altas[str(fila["id"])] = {
            **ficha,
            "id": str(fila["id"]),
            "origen": "alta",
            "slug": fila.get("slug") or None,
            # Horario: el texto de la ficha si existe; si no, se arma desde dias/abre/cierra del bot.
            "horario": ficha.get("horario") or horario_desde_ficha(
                ficha.get("dias"), ficha.get("abre"), ficha.get("cierra")
            ),
            "h3": fila.get("h3"),
            "lat": fila.get("lat"),
            "lng": fila.get("lng"),
        }
    return altas


def registros_base() -> list[dict]:
    """Directorio + altas combinados, sin ediciones de ficha (para buscar por slug)."""
    combinados = _base_directorio()
    for id_, alta in _altas().items():
        combinados[id_] = {**combinados.get(id_, {}), **alta}
    return list(combinados.values())


def _overrides(negocio_id: str) -> dict:
    datos = _leer_json(config.LIVE_DIR / "fichas" / f"{negocio_id}.json", {})
    return datos if isinstance(datos, dict) else {}


def get_negocio(negocio_id: str) -> dict | None:
    """Registro combinado: directorio, luego alta, luego ediciones de la ficha."""
    if not valid_id(negocio_id):
        return None
    base = _base_directorio().get(negocio_id)
    alta = _altas().get(negocio_id)
    if base is None and alta is None:
        return None
    registro = {**(base or {}), **(alta or {})}
    registro.update(_overrides(negocio_id))
    registro["id"] = negocio_id
    return registro


def guardar_ficha(negocio_id: str, cambios: dict) -> None:
    carpeta = config.LIVE_DIR / "fichas"
    carpeta.mkdir(parents=True, exist_ok=True)
    datos = {**_overrides(negocio_id), **cambios}
    (carpeta / f"{negocio_id}.json").write_text(
        json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def ficha_publica(rec: dict) -> dict:
    """Solo los campos de FICHA_CAMPOS, con valores por defecto seguros."""
    ficha = {campo: rec.get(campo) for campo in FICHA_CAMPOS}
    ficha["formas_pago"] = [str(f) for f in (ficha["formas_pago"] or [])]
    ficha["productos"] = [p for p in (ficha["productos"] or []) if isinstance(p, dict)]
    ficha["acepta_mercomuna"] = bool(ficha["acepta_mercomuna"])
    ficha["ubicacion"] = ficha["ubicacion"] or "aproximada"
    ficha["aparecer_en_rutas"] = True if ficha["aparecer_en_rutas"] is None else bool(
        ficha["aparecer_en_rutas"]
    )
    return ficha


def descripcion(ficha: dict) -> str:
    """Plantilla fija con datos de la ficha. Sin LLM, sin costo."""
    nombre = ficha.get("nombre") or "Este negocio"
    giro = ficha.get("giro")
    frase = f"{nombre} es un negocio de {giro.lower()}" if giro else f"{nombre} es un negocio de barrio"
    if ficha.get("colonia"):
        frase += f" en {ficha['colonia']}"
    partes = [frase + "."]
    nombres = [p["nombre"] for p in ficha.get("productos", []) if p.get("nombre")][:5]
    if nombres:
        partes.append(f"Vende {', '.join(nombres)}.")
    if ficha.get("horario"):
        partes.append(f"Horario: {ficha['horario']}.")
    if ficha.get("formas_pago"):
        partes.append(f"Acepta {', '.join(ficha['formas_pago'])}.")
    if ficha.get("acepta_mercomuna"):
        partes.append("Acepta Mercomuna.")
    return " ".join(partes)


def _simulado(negocio_id: str) -> dict[str, int]:
    semilla = int(hashlib.sha256(negocio_id.encode("utf-8")).hexdigest()[:12], 16)
    azar = random.Random(semilla)
    return {
        "busquedas": azar.randint(8, 60),
        "rutas": azar.randint(1, 12),
        "compre_aqui": azar.randint(0, 15),
        "visitas_pagina": azar.randint(3, 40),
    }


def avance(negocio_id: str, ahora: datetime | None = None) -> dict:
    """Avance de los últimos 7 días. Sin eventos reales del negocio: cifras simuladas y etiquetadas."""
    ahora = ahora or datetime.now(UTC)
    desde = ahora - timedelta(days=VENTANA_DIAS)
    conteos: Counter = Counter()
    for evento in _leer_jsonl(config.LIVE_DIR / "eventos.jsonl"):
        if evento.get("negocio_id") != negocio_id or evento.get("demo_data") is True:
            continue
        ts = _parse_ts(evento.get("ts"))
        tipo = evento.get("tipo")
        if ts is None or not (desde <= ts <= ahora) or tipo not in AVANCE_CLAVES:
            continue
        conteos[AVANCE_CLAVES[tipo]] += 1
    if sum(conteos.values()) > 0:
        cifras = {clave: conteos.get(clave, 0) for clave in AVANCE_CLAVES.values()}
        return {"tipo_dato": "real", "dias": VENTANA_DIAS, "conteos": cifras}
    return {
        "tipo_dato": "simulado",
        "dias": VENTANA_DIAS,
        "conteos": _simulado(negocio_id),
        "nota": "Cifras de ejemplo: aún no hay visitas ni apariciones reales de tu negocio.",
    }


def escalera(ficha: dict) -> list[dict]:
    """Escalera de barrio de 4 escalones con estado, beneficio y siguiente acción."""
    visible = bool(ficha.get("nombre"))
    pagos = " ".join(ficha.get("formas_pago") or []).lower()
    digital = any(clave in pagos for clave in ("transfer", "dimo", "codi"))
    return [
        {
            "orden": 1,
            "nombre": "Visible",
            "estado": "logrado" if visible else "siguiente",
            "beneficio": "Apareces en el mapa del barrio y en las rutas de compra.",
            "siguiente_accion": (
                "Pon tu cartel con QR en el puesto."
                if visible
                else "Completa el nombre y el giro de tu negocio."
            ),
        },
        {
            "orden": 2,
            "nombre": "Cobro digital",
            "estado": "logrado" if digital else ("siguiente" if visible else "pendiente"),
            "beneficio": "Tus clientes pagan con transferencia, DiMo o CoDi, sin comisión.",
            "siguiente_accion": (
                "Ya aceptas pagos digitales."
                if digital
                else "Activa DiMo o CoDi en la app de tu banco."
            ),
        },
        {
            "orden": 3,
            "nombre": "Historial",
            "estado": "proximamente",
            "beneficio": "Tu historial de pagos digitales te ayudará a tener más opciones.",
            "siguiente_accion": "Próximamente. No necesitas hacer nada todavía.",
        },
        {
            "orden": 4,
            "nombre": "Crédito",
            "estado": "horizonte",
            "beneficio": "Acceso a crédito para tu negocio con base en tu historial.",
            "siguiente_accion": "Se habilita cuando exista el historial.",
        },
    ]


def programas() -> list[dict]:
    """Programas de programas.json. Los 'por_verificar' no se muestran."""
    filas = _leer_json(config.PROCESSED_DIR / "programas.json", [])
    salida = []
    for p in filas if isinstance(filas, list) else []:
        if not isinstance(p, dict) or p.get("estado") == "por_verificar":
            continue
        salida.append(
            {
                "id": p.get("id"),
                "nombre": p.get("nombre"),
                "que_es": p.get("que_es"),
                "como_entrar": p.get("como_entrar"),
                "url_oficial": p.get("url_oficial"),
                "estado": p.get("estado"),
                "fecha_verificacion": p.get("fecha_verificacion"),
            }
        )
    return salida


def ficha_completa(negocio_id: str, ahora: datetime | None = None) -> dict | None:
    rec = get_negocio(negocio_id)
    if rec is None:
        return None
    ficha = ficha_publica(rec)
    slug = rec.get("pagina_slug") or rec.get("slug")
    return {
        "id": negocio_id,
        "origen": rec.get("origen"),
        "ficha": ficha,
        "descripcion": descripcion(ficha),
        "avance": avance(negocio_id, ahora),
        "escalera": escalera(ficha),
        "programas": programas(),
        "pagina": (
            {"url": f"/n/{slug}", "cartel": f"/n/{slug}/cartel"} if slug else None
        ),
    }

