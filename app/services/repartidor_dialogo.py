"""Alta de repartidor por Telegram (IDEA-v2 §4.2 y §4.5): máquina de estados sin dependencia de Telegram.

Cada paso acepta botón, texto o nota de voz (ya transcrita con `altas.transcribir`). El LLM solo EXTRAE el campo
pedido con salida estructurada validada con Pydantic y nunca produce una cifra visible: la disponibilidad sale de
opciones cerradas y la edad solo se valida, nunca se muestra. Con DEMO_MODE=1 (o sin llave) extrae con reglas locales.
La prioridad (18-30 + estudia) se calcula en el backend (`registrar_repartidor`) y no se le muestra a nadie.

Los modelos de abajo son locales y usan los nombres de campo de IDEA-v2 §7; se enchufan al contrato de
`app/schemas/` cuando CO-001 se integre.
"""

import hashlib
import json
import logging
import os
import random
import re
import time
import unicodedata
import uuid
from collections.abc import Callable
from datetime import date
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, ValidationError

from app import config
from app.config import settings
from app.services import altas

log = logging.getLogger(__name__)

TRANSPORTES = {
    "bici": "Bici",
    "bici_electrica": "Bici eléctrica",
    "a_pie": "A pie",
    "scooter_electrico": "Scooter eléctrico",
    "moto": "Moto",
    "auto": "Auto",
}
ECOLOGICOS = {"bici", "bici_electrica", "a_pie", "scooter_electrico"}
TIPOS_ID = {"ine": "INE", "pasaporte": "Pasaporte", "escolar": "Credencial escolar vigente"}
DIAS_OPC = {"entre_semana": ("Entre semana", [0, 1, 2, 3, 4]), "fin_de_semana": ("Fin de semana", [5, 6]),
            "todos": ("Todos los días", [0, 1, 2, 3, 4, 5, 6])}
FRANJAS = {"manana": ("Mañana", "07:00", "12:00"), "tarde": ("Tarde", "12:00", "18:00"),
           "noche": ("Noche", "18:00", "22:00")}
PESO_PRIORIDAD = {"edad_18_30": 1, "estudiante": 1}  # TODO: mover a app/config.py cuando se pueda editar (IDEA-v2 §4.3)

AVISO_PRIVACIDAD = (
    "🔒 Aviso de privacidad (resumen)\n"
    "Usamos tu nombre, tu rango de edad, si estudias, tu zona y tu transporte solo para ofrecerte rutas de entrega "
    "de negocios de barrio. Tu identificación se usa una vez para verificarte y no se publica ni se guarda como "
    "imagen. No guardamos tu teléfono: te escribimos por este chat. Puedes pedir que borremos tus datos cuando quieras.\n\n"
    "¿Aceptas?"
)

# Respaldo cuando data/processed/colonias.json aún no existe (fuente real por fijar, IDEA-v2 §5).
ALCALDIAS_LOCAL = [
    ("09003", "Coyoacán", True), ("09007", "Iztapalapa", True),
    ("09002", "Azcapotzalco", False), ("09010", "Álvaro Obregón", False), ("09014", "Benito Juárez", False),
    ("09015", "Cuauhtémoc", False), ("09004", "Cuajimalpa de Morelos", False), ("09005", "Gustavo A. Madero", False),
    ("09006", "Iztacalco", False), ("09008", "La Magdalena Contreras", False), ("09016", "Miguel Hidalgo", False),
    ("09009", "Milpa Alta", False), ("09011", "Tláhuac", False), ("09012", "Tlalpan", False),
    ("09017", "Venustiano Carranza", False), ("09013", "Xochimilco", False),
]
COLONIAS_LOCAL = {
    "09003": ["Del Carmen", "Santa Catarina", "Pedregal de Santo Domingo", "Los Reyes", "Ajusco", "Santo Domingo",
              "Copilco el Alto", "Villa Coyoacán"],
    "09007": ["Santa Martha Acatitla", "Escuadrón 201", "Paraje San Juan", "Cabeza de Juárez", "San Miguel Teotongo",
              "Santa Cruz Meyehualco", "Leyes de Reforma", "Ermita Zaragoza"],
}


# ---------- modelos (nombres de campo de IDEA-v2 §7) ----------

class RepartidorIn(BaseModel):
    """Lo que recibe `POST /api/repartidores`. La edad exacta y la prioridad no viajan ni se guardan."""
    chat_id: int
    nombre_mostrar: str = Field(min_length=2, max_length=40)
    rango_edad: Literal["18-30", "31+"]
    estudiante: bool
    alcaldia_cvegeo: str
    colonias: list[str] = Field(min_length=1, max_length=3)
    transporte: Literal["bici", "bici_electrica", "a_pie", "scooter_electrico", "moto", "auto"]
    dias: list[int]
    desde: str
    hasta: str
    id_verificada: bool = False
    tipo_id: str | None = None
    demo_data: bool = False


class NombreOut(BaseModel):
    nombre: str = Field(min_length=2, max_length=40, description="Como quiere que lo llamen, sin apellidos de más")


class EdadOut(BaseModel):
    edad: int | None = Field(None, ge=0, le=110, description="Años cumplidos; null si no la dijo")


class SiNoOut(BaseModel):
    valor: bool | None = Field(None, description="true = sí, false = no, null = no quedó claro")


class AlcaldiaOut(BaseModel):
    alcaldia: str | None = Field(None, description="Nombre de una alcaldía de la CDMX; null si no")


class ColoniasOut(BaseModel):
    colonias: list[str] = Field(default=[], max_length=3, description="Nombres de colonias tal como los dijo")


class TransporteOut(BaseModel):
    transporte: Literal["bici", "bici_electrica", "a_pie", "scooter_electrico", "moto", "auto"] | None = None


class DisponibilidadOut(BaseModel):
    dias: Literal["entre_semana", "fin_de_semana", "todos"] | None = None
    franja: Literal["manana", "tarde", "noche"] | None = None


class Sesion(BaseModel):
    """Estado de una conversación. Se guarda en `user_data` de Telegram como dict."""
    paso: str = "privacidad"
    chat_id: int = 0
    nombre: str | None = None
    rango_edad: str | None = None
    estudiante: bool | None = None
    tipo_id: str | None = None
    id_foto: str | None = None  # ruta temporal fuera de git; nunca sale de aquí
    alcaldia_cvegeo: str | None = None
    alcaldia_nombre: str | None = None
    colonias: list[str] = []
    colonias_nombres: list[str] = []
    transporte: str | None = None
    dias: str | None = None
    franja: str | None = None
    corrigiendo: bool = False
    demo_data: bool = False
    repartidor_id: str | None = None


Boton = tuple[str, str]  # (texto, callback_data)


class Respuesta(BaseModel):
    texto: str
    botones: list[list[Boton]] = []
    pide_foto: bool = False
    terminado: bool = False


class Entrada(BaseModel):
    texto: str | None = None
    boton: str | None = None
    foto: bytes | None = None
    audio: bytes | None = None


# ---------- catálogo ----------

def _norm(t: str) -> str:
    return unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower().strip()


def alcaldias() -> list[dict]:
    """Las 16 alcaldías, Coyoacán e Iztapalapa primero. Lee data/processed/colonias.json si existe."""
    try:
        datos = json.loads((config.PROCESSED_DIR / "colonias.json").read_text(encoding="utf-8"))
        filas = [
            {"cvegeo": a["alcaldia_cvegeo"], "nombre": a["alcaldia_nombre"], "prioridad": bool(a.get("prioridad")),
             "colonias": [{"id": c["id"], "nombre": c["nombre"]} for c in a.get("colonias", [])]}
            for a in datos
        ]
        if filas:
            return sorted(filas, key=lambda a: (not a["prioridad"], a["nombre"]))
    except (OSError, ValueError, KeyError, TypeError):
        pass
    return [
        {"cvegeo": cv, "nombre": n, "prioridad": p,
         "colonias": [{"id": f"{cv}-{altas.slugify(c)}", "nombre": c} for c in COLONIAS_LOCAL.get(cv, [])]}
        for cv, n, p in ALCALDIAS_LOCAL
    ]


def _alcaldia(cvegeo: str) -> dict | None:
    return next((a for a in alcaldias() if a["cvegeo"] == cvegeo), None)


# ---------- extracción: LLM con salida estructurada, o reglas locales ----------

def _llm(modelo: type[BaseModel], instruccion: str, texto: str):
    if altas.usar_respaldo():
        return None
    try:
        from openai import OpenAI

        cliente = OpenAI(api_key=settings.openai_api_key, timeout=30, max_retries=0)
        for nombre in (settings.openai_model, settings.openai_fallback_model):
            try:
                r = cliente.responses.parse(
                    model=nombre,
                    input=[
                        {"role": "system", "content": "Extrae SOLO el campo pedido de lo que dijo la persona. No inventes "
                         "nada; si no está claro, deja null. " + instruccion},
                        {"role": "user", "content": texto},
                    ],
                    text_format=modelo,
                )
                if r.output_parsed is not None:
                    return modelo.model_validate(r.output_parsed.model_dump())
            except (ValidationError, Exception) as e:  # noqa: BLE001 — un fallo del modelo no tumba el alta
                log.warning("extracción con %s falló: %s", nombre, e)
                if altas._sin_remedio(e):
                    break
    except Exception as e:  # noqa: BLE001
        log.warning("LLM no disponible: %s", e)
    return None


def _regla_nombre(t: str) -> NombreOut | None:
    limpio = re.sub(r"^(hola,?\s*)?(me llamo|mi nombre es|soy|me dicen|llámame|llamame)\s+", "", t.strip(), flags=re.IGNORECASE)
    limpio = re.sub(r"[^\w\sáéíóúüñÁÉÍÓÚÜÑ.'-]", "", limpio).strip(" .")
    limpio = " ".join(limpio.split()[:3]).title()
    try:
        return NombreOut(nombre=limpio) if re.search(r"[^\W\d_]{2}", limpio) else None
    except ValidationError:
        return None


def _regla_edad(t: str) -> EdadOut | None:
    m = re.search(r"\b(19\d{2}|20[0-2]\d)\b", t)  # año de nacimiento
    if m:
        return EdadOut(edad=date.today().year - int(m.group(1)))
    m = re.search(r"\b(\d{1,3})\b", t)
    if m and int(m.group(1)) <= 110:
        return EdadOut(edad=int(m.group(1)))
    palabras = {"dieciocho": 18, "diecinueve": 19, "veinte": 20, "veinticinco": 25, "treinta": 30, "cuarenta": 40}
    for p, n in palabras.items():
        if p in _norm(t):
            return EdadOut(edad=n)
    return None


def _regla_sino(t: str) -> SiNoOut:
    n = _norm(t)
    if re.search(r"\b(no|nel|nope|ninguna?|ya no|tampoco)\b", n):
        return SiNoOut(valor=False)
    if re.search(r"\b(si|sip|claro|asi es|estudio|aja|ok|acepto|afirmativo|simon|va)\b", n):
        return SiNoOut(valor=True)
    return SiNoOut(valor=None)


def _regla_alcaldia(t: str) -> AlcaldiaOut:
    n = _norm(t)
    for a in alcaldias():
        if _norm(a["nombre"]) in n or n in _norm(a["nombre"]) and len(n) > 4:
            return AlcaldiaOut(alcaldia=a["nombre"])
    return AlcaldiaOut()


def _regla_transporte(t: str) -> TransporteOut:
    n = _norm(t)
    if re.search(r"(bici|bicicleta|bike)", n) and re.search(r"(electric|motor)", n):
        return TransporteOut(transporte="bici_electrica")
    if re.search(r"scooter|patin", n):
        return TransporteOut(transporte="scooter_electrico")
    if re.search(r"bici|bicicleta|bike", n):
        return TransporteOut(transporte="bici")
    if re.search(r"a pie|caminando|camino|pie\b", n):
        return TransporteOut(transporte="a_pie")
    if re.search(r"moto", n):
        return TransporteOut(transporte="moto")
    if re.search(r"auto|carro|coche", n):
        return TransporteOut(transporte="auto")
    return TransporteOut()


def _regla_disp(t: str) -> DisponibilidadOut:
    n = _norm(t)
    dias = franja = None
    if re.search(r"fin de semana|fines de semana|sabado|domingo|findes", n):
        dias = "fin_de_semana"
    elif re.search(r"entre semana|lunes a viernes|de lunes", n):
        dias = "entre_semana"
    elif re.search(r"todos los dias|diario|toda la semana|cualquier dia|todos", n):
        dias = "todos"
    if re.search(r"manana|temprano|mediodia", n):
        franja = "manana"
    elif re.search(r"tarde", n):
        franja = "tarde"
    elif re.search(r"noche|nocturno", n):
        franja = "noche"
    return DisponibilidadOut(dias=dias, franja=franja)


def _colonias_de(alc: dict, t: str) -> list[tuple[str, str]]:
    """Colonias dichas por la persona → (id, nombre). Con catálogo, solo las que existen; sin él, texto libre."""
    pedazos = [p.strip() for p in re.split(r",|;|\sy\s|\se\s|\n", t) if p.strip()]
    salida: list[tuple[str, str]] = []
    for p in pedazos:
        n = _norm(p)
        if len(n) < 3:
            continue
        if alc["colonias"]:
            for c in alc["colonias"]:
                if n in _norm(c["nombre"]) or _norm(c["nombre"]) in n:
                    salida.append((c["id"], c["nombre"]))
                    break
        else:
            salida.append((f"{alc['cvegeo']}-{altas.slugify(p)}", p.title()))
    return salida


# ---------- ID, verificación y registro ----------

def carpeta_ids() -> Path:
    return config.LIVE_DIR / "ids"


def guardar_foto_id(foto: bytes) -> str:
    carpeta_ids().mkdir(parents=True, exist_ok=True)
    ruta = carpeta_ids() / f"{uuid.uuid4().hex}.jpg"
    ruta.write_bytes(foto)
    return str(ruta)


def verificar_id(ruta: str) -> bool:
    """En demo la verificación está simulada (demo_data: true): se da por buena y se BORRA la imagen.
    Fuera de demo la revisa una persona y la imagen se queda en data/live/ids/ (ignorado por git) hasta entonces."""
    if settings.demo_mode:
        Path(ruta).unlink(missing_ok=True)
        return True
    return False


def _nuevo_id(existentes: set[str]) -> str:
    while True:
        rid = f"R-{random.randint(0, 99999):05d}"
        if rid not in existentes:
            return rid


def prioridad(rango_edad: str, estudiante: bool) -> int:
    """Solo backend. 2 = 18-30 y estudiante; 1 = cumple una; 0 = ninguna (IDEA-v2 §4.3)."""
    return (PESO_PRIORIDAD["edad_18_30"] if rango_edad == "18-30" else 0) + (
        PESO_PRIORIDAD["estudiante"] if estudiante else 0)


class AdaptadorLocal:
    """Sustituto de POST /api/repartidores (CO-005): guarda en data/live/repartidores.jsonl."""

    def registrar(self, datos: RepartidorIn) -> dict:
        ruta = config.LIVE_DIR / "repartidores.jsonl"
        rid = _nuevo_id({f.get("id", "") for f in altas._jsonl(ruta)})
        fila = {
            "id": rid, "ts_alta": time.time(),
            "chat_id_hash": hashlib.sha256(f"colonia:{datos.chat_id}".encode()).hexdigest()[:16],
            "nombre_mostrar": datos.nombre_mostrar, "rango_edad": datos.rango_edad, "estudiante": datos.estudiante,
            "alcaldia_cvegeo": datos.alcaldia_cvegeo, "colonias": datos.colonias, "transporte": datos.transporte,
            "disponibilidad": {"dias": datos.dias, "desde": datos.desde, "hasta": datos.hasta},
            "id_verificada": datos.id_verificada, "tipo_id": datos.tipo_id,
            "estado": "activo" if datos.id_verificada else "pendiente_verificacion",
            "negocio_id": None, "prioridad": prioridad(datos.rango_edad, datos.estudiante),
            "rutas_completadas": 0, "demo_data": datos.demo_data,
        }
        altas._append(ruta, fila)
        return fila


class AdaptadorApi:
    """POST a la API real de CO-005 (REPARTIDORES_API_URL, p. ej. http://localhost:8000/api/repartidores)."""

    def __init__(self, url: str):
        self.url = url

    def registrar(self, datos: RepartidorIn) -> dict:
        import httpx

        r = httpx.post(self.url, json=datos.model_dump(), timeout=15)
        r.raise_for_status()
        return r.json()


def adaptador_por_defecto():
    url = os.environ.get("REPARTIDORES_API_URL", "")
    return AdaptadorApi(url) if url and not settings.demo_mode else AdaptadorLocal()


def registrar_repartidor(datos: RepartidorIn, adaptador=None) -> dict:
    """Punto único de alta. Cambia de adaptador sin tocar el diálogo."""
    return (adaptador or adaptador_por_defecto()).registrar(datos)


# ---------- diálogo ----------

def _si_no(pref: str) -> list[list[Boton]]:
    return [[("Sí", f"{pref}:si"), ("No", f"{pref}:no")]]


def iniciar(chat_id: int) -> tuple[Sesion, Respuesta]:
    ses = Sesion(chat_id=chat_id, demo_data=settings.demo_mode or altas.usar_respaldo())
    return ses, Respuesta(texto=AVISO_PRIVACIDAD, botones=[[("✅ Acepto", "acepto"), ("No acepto", "no_acepto")]])


def _preg_alcaldia() -> Respuesta:
    filas, fila = [], []
    for a in alcaldias():
        fila.append((a["nombre"], f"alc:{a['cvegeo']}"))
        if len(fila) == 2:
            filas.append(fila)
            fila = []
    if fila:
        filas.append(fila)
    return Respuesta(texto="¿En qué alcaldía quieres repartir? Toca una o dímela (texto o voz).", botones=filas)


def _preg_colonias(ses: Sesion) -> Respuesta:
    alc = _alcaldia(ses.alcaldia_cvegeo or "")
    elegidas = ", ".join(ses.colonias_nombres) or "ninguna todavía"
    if alc and alc["colonias"]:
        filas = [[(("✅ " if c["id"] in ses.colonias else "") + c["nombre"], f"col:{c['id']}")]
                 for c in alc["colonias"][:8]]
        if ses.colonias:
            filas.append([("Listo", "col_ok")])
        return Respuesta(texto=f"Elige hasta 3 colonias de {alc['nombre']} (o escríbelas / dímelas por voz).\n"
                               f"Llevas: {elegidas}.", botones=filas)
    return Respuesta(texto=f"Dime hasta 3 colonias de {ses.alcaldia_nombre} donde quieres repartir (texto o voz).\n"
                           f"Llevas: {elegidas}.",
                     botones=[[("Listo", "col_ok")]] if ses.colonias else [])


def _preg_transporte() -> Respuesta:
    claves = list(TRANSPORTES)
    return Respuesta(texto="¿En qué te mueves para repartir?",
                     botones=[[(TRANSPORTES[k], f"tr:{k}") for k in claves[i:i + 2]] for i in range(0, 6, 2)])


def _preg_dias() -> Respuesta:
    return Respuesta(texto="¿Qué días puedes? (puedes decir también la franja: mañana, tarde o noche)",
                     botones=[[(v[0], f"dias:{k}")] for k, v in DIAS_OPC.items()])


def _preg_franja() -> Respuesta:
    return Respuesta(texto="¿En qué horario?", botones=[[(f"{v[0]} ({v[1]}–{v[2]})", f"fr:{k}")] for k, v in FRANJAS.items()])


def _resumen(ses: Sesion) -> Respuesta:
    transporte = TRANSPORTES.get(ses.transporte or "", "")
    dias = DIAS_OPC[ses.dias or "todos"][0]
    fr = FRANJAS[ses.franja or "tarde"]
    texto = (
        "Así quedaría tu registro:\n\n"
        f"👤 {ses.nombre}\n"
        f"🎓 Estudias: {'sí' if ses.estudiante else 'no'}\n"
        f"🪪 Identificación: {TIPOS_ID.get(ses.tipo_id or '', '')} (recibida)\n"
        f"📍 {ses.alcaldia_nombre}: {', '.join(ses.colonias_nombres)}\n"
        f"🚲 Transporte: {transporte}\n"
        f"🕒 {dias}, {fr[0].lower()} ({fr[1]}–{fr[2]})\n\n¿Así queda?"
    )
    return Respuesta(texto=texto, botones=[[("✅ Así queda", "ok"), ("✏️ Corregir", "corregir")]])


_CAMPOS_CORREGIR = [("Nombre", "nombre"), ("Estudio", "estudia"), ("Alcaldía y colonias", "alcaldia"),
                    ("Transporte", "transporte"), ("Disponibilidad", "dias")]


def _tras_paso(ses: Sesion, siguiente: Callable[[], Respuesta], paso_sig: str) -> Respuesta:
    """Si venimos de 'Corregir' volvemos al resumen; si no, seguimos al paso siguiente."""
    if ses.corrigiendo:
        ses.corrigiendo = False
        ses.paso = "resumen"
        return _resumen(ses)
    ses.paso = paso_sig
    return siguiente()


def _ir_a(ses: Sesion, paso: str) -> Respuesta:
    ses.paso = paso
    return {
        "nombre": lambda: Respuesta(texto="¿Cómo quieres que te llamemos? (texto o nota de voz)"),
        "edad": lambda: Respuesta(texto="¿Cuántos años tienes? Basta con el número."),
        "estudia": lambda: Respuesta(texto="¿Estudias actualmente?", botones=_si_no("est")),
        "id_tipo": lambda: Respuesta(
            texto="Necesito verificar tu identidad. ¿Qué identificación vas a mandar?",
            botones=[[(v, f"id:{k}")] for k, v in TIPOS_ID.items()]),
        "id_foto": lambda: Respuesta(
            texto="Mándame una foto clara de tu identificación. La uso solo para verificarte, no se publica "
                  "y se borra después; solo guardamos que quedó verificada.", pide_foto=True),
        "alcaldia": _preg_alcaldia,
        "colonias": lambda: _preg_colonias(ses),
        "transporte": _preg_transporte,
        "dias": _preg_dias,
        "franja": _preg_franja,
        "resumen": lambda: _resumen(ses),
    }[paso]()


def _texto_de(ent: Entrada, transcriptor: Callable[[bytes], tuple[str, bool]]) -> str | None:
    if ent.texto:
        return ent.texto
    if ent.audio:
        return transcriptor(ent.audio)[0]
    return None


def avanzar(ses: Sesion, ent: Entrada, transcriptor: Callable[[bytes], tuple[str, bool]] | None = None,
            base_url: str = "http://localhost:8000", adaptador=None) -> Respuesta:
    """Un paso del diálogo. Muta `ses` y devuelve qué decir. Nunca lanza por entradas raras: repregunta."""
    transcriptor = transcriptor or altas.transcribir
    paso, b = ses.paso, ent.boton
    texto = None if b else _texto_de(ent, transcriptor)
    n = _norm(texto or "")

    if paso == "fin":
        return Respuesta(texto="Tu registro ya quedó. Si quieres empezar otro, escribe /start.", terminado=True)

    if paso == "privacidad":
        acepta = b == "acepto" or (b is None and texto and re.search(r"\bacepto\b", n))
        if acepta:
            return _ir_a(ses, "nombre")
        if b == "no_acepto" or (texto and re.search(r"\bno acepto\b|\bno quiero\b", n)):
            ses.paso = "fin"
            return Respuesta(texto="Sin tu aceptación no puedo seguir, y no guardé nada. Cuando quieras, escribe /start.",
                             terminado=True)
        return Respuesta(texto="Para seguir necesito que aceptes el aviso de privacidad.",
                         botones=[[("✅ Acepto", "acepto"), ("No acepto", "no_acepto")]])

    if paso == "nombre":
        out = (_llm(NombreOut, "Campo: el nombre con el que quiere que le llamen.", texto) if texto else None) \
            or (_regla_nombre(texto) if texto else None)
        if not out:
            return Respuesta(texto="No alcancé a entender tu nombre. ¿Cómo te llamas?")
        ses.nombre = out.nombre
        return _tras_paso(ses, lambda: _ir_a(ses, "edad"), "edad")

    if paso == "edad":
        out = (_llm(EdadOut, "Campo: edad en años cumplidos (si dio año de nacimiento, calcula con 2026).", texto)
               if texto else None) or (_regla_edad(texto) if texto else None)
        if not out or out.edad is None:
            return Respuesta(texto="¿Cuántos años tienes? Dime solo el número.")
        if out.edad < 18:
            ses.paso = "fin"
            return Respuesta(texto="Por ahora el registro es solo para mayores de 18 años. Gracias por tu interés, "
                                   "no guardé ningún dato.", terminado=True)
        ses.rango_edad = "18-30" if out.edad <= 30 else "31+"  # la edad exacta se descarta
        return _ir_a(ses, "estudia")

    if paso == "estudia":
        if b in ("est:si", "est:no"):
            val = b == "est:si"
        else:
            val = (_llm(SiNoOut, "Campo: ¿estudia actualmente?", texto) if texto else None) or \
                (_regla_si_no_texto(texto))
            val = val.valor if val else None
        if val is None:
            return Respuesta(texto="¿Estudias actualmente? Toca Sí o No.", botones=_si_no("est"))
        ses.estudiante = val
        return _tras_paso(ses, lambda: _ir_a(ses, "id_tipo"), "id_tipo")

    if paso == "id_tipo":
        clave = b.split(":", 1)[1] if b and b.startswith("id:") else None
        if clave is None and texto:
            clave = "pasaporte" if "pasaporte" in n else "escolar" if re.search(r"escolar|escuela|credencial", n) \
                else "ine" if re.search(r"\bine\b|\bife\b|electoral", n) else None
        if clave not in TIPOS_ID:
            return _ir_a(ses, "id_tipo")
        ses.tipo_id = clave
        return _ir_a(ses, "id_foto")

    if paso == "id_foto":
        if not ent.foto:
            return Respuesta(texto="Necesito la foto de tu identificación (no vale texto ni voz).", pide_foto=True)
        ses.id_foto = guardar_foto_id(ent.foto)
        return _tras_paso(ses, lambda: _ir_a(ses, "alcaldia"), "alcaldia")

    if paso == "alcaldia":
        cv = b.split(":", 1)[1] if b and b.startswith("alc:") else None
        if cv is None and texto:
            nombre = ((_llm(AlcaldiaOut, "Campo: alcaldía de la CDMX.", texto) or _regla_alcaldia(texto)).alcaldia)
            cv = next((a["cvegeo"] for a in alcaldias() if nombre and _norm(a["nombre"]) == _norm(nombre)), None)
        alc = _alcaldia(cv or "")
        if not alc:
            return _preg_alcaldia()
        if alc["cvegeo"] != ses.alcaldia_cvegeo:
            ses.colonias, ses.colonias_nombres = [], []
        ses.alcaldia_cvegeo, ses.alcaldia_nombre = alc["cvegeo"], alc["nombre"]
        return _ir_a(ses, "colonias")  # las colonias siempre se piden tras elegir alcaldía

    if paso == "colonias":
        alc = _alcaldia(ses.alcaldia_cvegeo or "")
        if b == "col_ok" or (texto and re.fullmatch(r"(listo|ya|eso es todo|ya estuvo)\.?", n)):
            if not ses.colonias:
                return _preg_colonias(ses)
            return _siguiente_de_colonias(ses)
        nuevas: list[tuple[str, str]] = []
        if b and b.startswith("col:") and alc:
            cid = b.split(":", 1)[1]
            nuevas = [(c["id"], c["nombre"]) for c in alc["colonias"] if c["id"] == cid]
            if cid in ses.colonias:  # tocar de nuevo la quita
                i = ses.colonias.index(cid)
                ses.colonias.pop(i)
                ses.colonias_nombres.pop(i)
                return _preg_colonias(ses)
        elif texto and alc:
            llm = _llm(ColoniasOut, "Campo: colonias que dijo (máximo 3).", texto)
            nuevas = _colonias_de(alc, ", ".join(llm.colonias) if llm and llm.colonias else texto)
        if not nuevas:
            return Respuesta(texto="No encontré esa colonia. Prueba con otro nombre o toca una de la lista.",
                             botones=_preg_colonias(ses).botones)
        for cid, nombre in nuevas:
            if cid not in ses.colonias and len(ses.colonias) < 3:
                ses.colonias.append(cid)
                ses.colonias_nombres.append(nombre)
        if len(ses.colonias) >= 3:
            return _siguiente_de_colonias(ses)
        return _preg_colonias(ses)

    if paso == "transporte":
        clave = b.split(":", 1)[1] if b and b.startswith("tr:") else None
        if clave is None and texto:
            llm = _llm(TransporteOut, "Campo: medio de transporte para repartir.", texto)
            clave = (llm or _regla_transporte(texto)).transporte
        if clave not in TRANSPORTES:
            return _preg_transporte()
        ses.transporte = clave
        sig = _tras_paso(ses, lambda: _ir_a(ses, "dias"), "dias")
        if clave in ECOLOGICOS:
            msg = "🌱 ¡Excelente elección! Repartir limpio cuida el aire de tu barrio."
        else:
            msg = ("🚲 Ojo: en barrio la bici suele ser más rápida y barata que moto o auto, cuida el aire, y quienes "
                   "reparten en bici juntan premios por rutas completadas, incluida una bici. Tu elección queda "
                   "como la pusiste; puedes cambiarla cuando quieras.")
        sig.texto = msg + "\n\n" + sig.texto
        return sig

    if paso in ("dias", "franja"):
        dias = franja = None
        if b and b.startswith("dias:"):
            dias = b.split(":", 1)[1]
        elif b and b.startswith("fr:"):
            franja = b.split(":", 1)[1]
        elif texto:
            d = _llm(DisponibilidadOut, "Campos: días (entre_semana, fin_de_semana, todos) y franja "
                     "(manana, tarde, noche) que dijo.", texto) or _regla_disp(texto)
            dias, franja = d.dias, d.franja
        if dias in DIAS_OPC:
            ses.dias = dias
        if franja in FRANJAS:
            ses.franja = franja
        if not ses.dias:
            return _preg_dias()
        if not ses.franja:
            ses.paso = "franja"
            return _preg_franja()
        if ses.corrigiendo:
            ses.corrigiendo = False
        return _ir_a(ses, "resumen")

    if paso == "resumen":
        if b == "ok" or (texto and re.search(r"\b(asi queda|si|ok|correcto|confirmo)\b", n) and "no" not in n.split()):
            return _confirmar(ses, base_url, adaptador)
        if b == "corregir" or (texto and re.search(r"corregir|cambiar|no", n)):
            return Respuesta(texto="¿Qué quieres corregir?",
                             botones=[[(t, f"fix:{k}")] for t, k in _CAMPOS_CORREGIR])
        if b and b.startswith("fix:"):
            ses.corrigiendo = True
            destino = b.split(":", 1)[1]
            if destino == "dias":
                ses.dias = ses.franja = None
            return _ir_a(ses, destino)
        return _resumen(ses)

    return Respuesta(texto="Escribe /start para empezar.", terminado=True)


def _regla_si_no_texto(texto: str | None) -> SiNoOut | None:
    return _regla_sino(texto) if texto else None


def _siguiente_de_colonias(ses: Sesion) -> Respuesta:
    if ses.corrigiendo:
        ses.corrigiendo = False
        ses.paso = "resumen"
        return _resumen(ses)
    return _ir_a(ses, "transporte")


def _confirmar(ses: Sesion, base_url: str, adaptador) -> Respuesta:
    verificada = verificar_id(ses.id_foto) if ses.id_foto else False
    datos = RepartidorIn(
        chat_id=ses.chat_id, nombre_mostrar=ses.nombre or "", rango_edad=ses.rango_edad or "31+",  # type: ignore[arg-type]
        estudiante=bool(ses.estudiante), alcaldia_cvegeo=ses.alcaldia_cvegeo or "", colonias=ses.colonias,
        transporte=ses.transporte or "bici",  # type: ignore[arg-type]
        dias=DIAS_OPC[ses.dias or "todos"][1], desde=FRANJAS[ses.franja or "tarde"][1],
        hasta=FRANJAS[ses.franja or "tarde"][2], id_verificada=verificada, tipo_id=ses.tipo_id,
        demo_data=ses.demo_data or settings.demo_mode,
    )
    try:
        fila = registrar_repartidor(datos, adaptador)
    except Exception as e:  # noqa: BLE001 — la API caída no pierde la sesión
        log.warning("registrar_repartidor falló: %s", e)
        return Respuesta(texto="No pude guardar tu registro ahora. Toca otra vez en un momento.",
                         botones=[[("✅ Así queda", "ok"), ("✏️ Corregir", "corregir")]])
    ses.repartidor_id = fila["id"]
    if ses.id_foto and not verificada:  # la revisa una persona: la imagen queda atada al número, fuera de git
        destino = carpeta_ids() / f"{fila['id']}.jpg"
        Path(ses.id_foto).replace(destino)
    ses.id_foto = None
    ses.paso = "fin"
    nota = "\n\n(registro de ejemplo: datos de demostración)" if datos.demo_data else ""
    return Respuesta(
        texto=f"🎉 ¡Listo, {ses.nombre}! Tu número de repartidor es {fila['id']}.\n"
              f"Entra al portal: {base_url.rstrip('/')}/#/repartidor\n"
              "Para entrar usa tu número y el código que te mando por aquí cuando lo pidas." + nota,
        terminado=True)
