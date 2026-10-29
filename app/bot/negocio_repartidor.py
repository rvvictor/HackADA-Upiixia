"""Tras "Así queda" del alta de negocio: ¿tienes a alguien que haga entregas? (IDEA-v2.md §6).

- **Sí → Lo doy de alta yo**: las preguntas de §4.2 (`repartidor_dialogo`) a nombre del repartidor, sin aviso de
  privacidad ni foto de identificación; queda `pendiente_verificacion` y ligado al `negocio_id`.
- **Sí → Le mando un link**: `t.me/<bot>?start=inv_<token>`; el repartidor termina su alta él mismo, con identificación
  y consentimiento propios. `resolver_invitacion` da el `negocio_id` del token.
- **No**: se le ofrece la red de repartidores del barrio.

La lógica es pura (`preguntar` / `avanzar`); los handlers de Telegram al final solo la conectan. Integración en
`app/bot/__main__.py`: al terminar el alta llamar `iniciar(update, context, alta.id)`, y en `/start inv_<token>`
usar `resolver_invitacion(token)` para ligar el alta del repartidor al negocio.
"""

import json
import secrets
import time
from pathlib import Path

from pydantic import BaseModel
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import ContextTypes

from app import config
from app.services import altas
from app.services import repartidor_dialogo as rd

CLAVE = "neg_rep"
VIGENCIA_INVITACION_S = 7 * 24 * 3600
PREGUNTA = "¿Tienes a alguien que haga entregas para tu negocio?"
RED_BARRIO = ("Va. Cuando tengas un pedido, lo publicamos para repartidores de tu colonia, "
              "sin comisiones de plataforma. 🚲")


class SesionNegocio(BaseModel):
    """Estado del sub-diálogo; se guarda en `user_data` de Telegram como dict."""
    paso: str = "pregunta"  # pregunta → opcion → alta (repartidor_dialogo) | fin
    negocio_id: str
    chat_id: int = 0
    rep: rd.Sesion | None = None


def _ruta_invitaciones() -> Path:
    return config.LIVE_DIR / "invitaciones.jsonl"


def crear_invitacion(negocio_id: str, bot_username: str, ahora: float | None = None) -> dict:
    """Guarda el token en `data/live/invitaciones.jsonl` y devuelve la forma de `InvitacionResponse` (CO-001)."""
    ahora = time.time() if ahora is None else ahora
    token = secrets.token_urlsafe(8).replace("-", "").replace("_", "")[:10]
    fila = {"token": token, "negocio_id": negocio_id, "ts": ahora, "expira_ts": ahora + VIGENCIA_INVITACION_S}
    altas._append(_ruta_invitaciones(), fila)
    return {"token": token, "link": f"https://t.me/{bot_username}?start=inv_{token}", "negocio_id": negocio_id,
            "expira_ts": fila["expira_ts"]}


def resolver_invitacion(token: str, ahora: float | None = None) -> str | None:
    """`inv_<token>` (o solo el token) → `negocio_id`, o None si no existe o ya venció."""
    token = token.removeprefix("inv_")
    ahora = time.time() if ahora is None else ahora
    for fila in reversed(altas._jsonl(_ruta_invitaciones())):
        if fila.get("token") == token:
            return fila["negocio_id"] if fila.get("expira_ts", 0) > ahora else None
    return None


def ligar_a_negocio(repartidor_id: str, negocio_id: str) -> None:
    """Pone `negocio_id` en la fila del repartidor de `data/live/repartidores.jsonl`."""
    ruta = config.LIVE_DIR / "repartidores.jsonl"
    filas = altas._jsonl(ruta)
    for fila in filas:
        if fila.get("id") == repartidor_id:
            fila["negocio_id"] = negocio_id
    ruta.write_text("".join(json.dumps(f, ensure_ascii=False) + "\n" for f in filas), encoding="utf-8")


class AdaptadorNegocio:
    """Registra con el adaptador de siempre y deja al repartidor ligado al negocio."""

    def __init__(self, negocio_id: str, base=None):
        self.negocio_id = negocio_id
        self.base = base or rd.adaptador_por_defecto()

    def registrar(self, datos: rd.RepartidorIn) -> dict:
        if isinstance(self.base, rd.AdaptadorApi):  # la API (CO-005) recibe negocio_id en el alta
            import httpx

            r = httpx.post(self.base.url, json={**datos.model_dump(), "negocio_id": self.negocio_id}, timeout=15)
            r.raise_for_status()
            return r.json()
        fila = self.base.registrar(datos)
        if isinstance(self.base, rd.AdaptadorLocal):
            ligar_a_negocio(fila["id"], self.negocio_id)
        return {**fila, "negocio_id": self.negocio_id}


def primero_su_negocio(ofertas: list[dict], negocio_id: str | None) -> list[dict]:
    """Las rutas del negocio del repartidor van antes que la cola general; el resto conserva su orden (§4.3)."""
    if not negocio_id:
        return list(ofertas)
    return sorted(ofertas, key=lambda o: o.get("negocio_id") != negocio_id)


def preguntar(negocio_id: str, chat_id: int = 0) -> tuple[SesionNegocio, rd.Respuesta]:
    ses = SesionNegocio(negocio_id=negocio_id, chat_id=chat_id)
    return ses, rd.Respuesta(texto=PREGUNTA, botones=[[("Sí", "nr:si"), ("No", "nr:no")]])


def _opciones() -> rd.Respuesta:
    return rd.Respuesta(
        texto="¿Cómo lo registramos?\n• Lo doy de alta yo: te hago las preguntas por él o ella, sin identificación; "
              "queda pendiente de verificar.\n• Le mando un link: abre el bot y termina su alta con su identificación.",
        botones=[[("Lo doy de alta yo", "nr:yo")], [("Le mando un link", "nr:link")]])


def avanzar(ses: SesionNegocio, ent: rd.Entrada, bot_username: str = "<bot>", base_url: str = "http://localhost:8000",
            transcriptor=None, adaptador=None) -> rd.Respuesta:
    """Un paso. Muta `ses`. En el paso `alta` delega en `repartidor_dialogo` y se salta la identificación."""
    b = ent.boton
    texto = rd._norm(ent.texto) if ent.texto and not b else ""

    if ses.paso == "pregunta":
        if b == "nr:no" or texto.startswith("no"):
            ses.paso = "fin"
            return rd.Respuesta(texto=RED_BARRIO, terminado=True)
        if b == "nr:si" or texto.startswith("si"):
            ses.paso = "opcion"
            return _opciones()
        return rd.Respuesta(texto=PREGUNTA + " Toca Sí o No.", botones=[[("Sí", "nr:si"), ("No", "nr:no")]])

    if ses.paso == "opcion":
        if b == "nr:link" or "link" in texto:
            inv = crear_invitacion(ses.negocio_id, bot_username)
            ses.paso = "fin"
            return rd.Respuesta(
                texto="Mándale este link a tu repartidor. Al abrirlo termina su alta con su identificación y queda "
                      f"ligado a tu negocio:\n{inv['link']}\n(vale 7 días)", terminado=True)
        if b == "nr:yo" or "yo" in texto.split():
            ses.paso = "alta"
            ses.rep = rd.Sesion(chat_id=ses.chat_id, demo_data=config.settings.demo_mode or altas.usar_respaldo())
            r = rd._ir_a(ses.rep, "nombre")
            return rd.Respuesta(texto="Va, te pregunto por tu repartidor. " + r.texto, botones=r.botones)
        return _opciones()

    if ses.paso == "alta" and ses.rep is not None:
        r = rd.avanzar(ses.rep, ent, transcriptor, base_url=base_url,
                       adaptador=AdaptadorNegocio(ses.negocio_id, adaptador))
        if ses.rep.paso in ("id_tipo", "id_foto"):  # el negocio no manda identificación ajena
            ses.rep.tipo_id = ses.rep.id_foto = None
            r = rd._tras_paso(ses.rep, lambda: rd._ir_a(ses.rep, "alcaldia"), "alcaldia")
        if ses.rep.paso == "fin":
            ses.paso = "fin"
            if ses.rep.repartidor_id:
                return rd.Respuesta(
                    texto=r.texto + "\n\nQuedó ligado a tu negocio y pendiente de verificar su identidad. "
                                    "Sus rutas de tu negocio le llegan primero.", terminado=True)
        return r

    ses.paso = "fin"
    return rd.Respuesta(texto="Listo. Si quieres registrar a alguien más, escribe /start.", terminado=True)


# ---------- Telegram ----------

def activo(context: ContextTypes.DEFAULT_TYPE) -> bool:
    d = context.user_data.get(CLAVE)
    return bool(d) and d.get("paso") != "fin"


def _teclado(r: rd.Respuesta) -> InlineKeyboardMarkup | None:
    if not r.botones:
        return None
    return InlineKeyboardMarkup([[InlineKeyboardButton(t, callback_data=c) for t, c in fila] for fila in r.botones])


async def _decir(update: Update, r: rd.Respuesta) -> None:
    await update.effective_message.reply_text(r.texto, reply_markup=_teclado(r) or ReplyKeyboardRemove())


async def iniciar(update: Update, context: ContextTypes.DEFAULT_TYPE, negocio_id: str) -> None:
    ses, r = preguntar(negocio_id, update.effective_chat.id)
    context.user_data[CLAVE] = ses.model_dump()
    await _decir(update, r)


async def _paso(update: Update, context: ContextTypes.DEFAULT_TYPE, ent: rd.Entrada) -> None:
    from app.bot.repartidor import BASE_URL

    ses = SesionNegocio.model_validate(context.user_data[CLAVE])
    r = avanzar(ses, ent, bot_username=context.bot.username or "<bot>", base_url=BASE_URL)
    context.user_data[CLAVE] = ses.model_dump()
    await _decir(update, r)
    if r.terminado:
        context.user_data.pop(CLAVE, None)


async def texto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _paso(update, context, rd.Entrada(texto=update.message.text))


async def voz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    archivo = await (update.message.voice or update.message.audio).get_file()
    transcrito, grabada = altas.transcribir(bytes(await archivo.download_as_bytearray()))
    await update.message.reply_text(f"🎙️ Escuché: “{transcrito}”" + (" (ejemplo grabado)" if grabada else ""))
    await _paso(update, context, rd.Entrada(texto=transcrito))


async def boton(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    await q.edit_message_reply_markup(None)
    await _paso(update, context, rd.Entrada(boton=q.data))
