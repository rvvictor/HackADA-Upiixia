"""Handlers de Telegram para el alta de repartidor. Toda la lógica vive en `app.services.repartidor_dialogo`."""

import os

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import ContextTypes

from app.services import altas
from app.services import repartidor_dialogo as rd

CLAVE = "rep"
BASE_URL = os.environ.get("PUBLIC_BASE_URL", "http://localhost:8000").rstrip("/")


def activo(context: ContextTypes.DEFAULT_TYPE) -> bool:
    d = context.user_data.get(CLAVE)
    return bool(d) and d.get("paso") != "fin"


def _teclado(r: rd.Respuesta) -> InlineKeyboardMarkup | None:
    if not r.botones:
        return None
    return InlineKeyboardMarkup([[InlineKeyboardButton(t, callback_data=c) for t, c in fila] for fila in r.botones])


async def _decir(update: Update, r: rd.Respuesta) -> None:
    await update.effective_message.reply_text(r.texto, reply_markup=_teclado(r) or ReplyKeyboardRemove())


async def iniciar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    ses, r = rd.iniciar(update.effective_chat.id)
    context.user_data.clear()
    context.user_data[CLAVE] = ses.model_dump()
    await _decir(update, r)


async def _paso(update: Update, context: ContextTypes.DEFAULT_TYPE, ent: rd.Entrada) -> None:
    ses = rd.Sesion.model_validate(context.user_data[CLAVE])
    r = rd.avanzar(ses, ent, base_url=BASE_URL)
    context.user_data[CLAVE] = ses.model_dump()
    await _decir(update, r)
    if r.terminado:
        context.user_data.pop(CLAVE, None)


async def texto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _paso(update, context, rd.Entrada(texto=update.message.text))


async def voz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    archivo = await (update.message.voice or update.message.audio).get_file()
    audio = bytes(await archivo.download_as_bytearray())
    transcrito, grabada = altas.transcribir(audio)
    await update.message.reply_text(f"🎙️ Escuché: “{transcrito}”" + (" (ejemplo grabado)" if grabada else ""))
    await _paso(update, context, rd.Entrada(texto=transcrito))


async def foto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    archivo = await update.message.photo[-1].get_file()
    await _paso(update, context, rd.Entrada(foto=bytes(await archivo.download_as_bytearray())))


async def boton(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    if not context.user_data.get(CLAVE):
        await q.message.reply_text("Esta conversación ya terminó. Escribe /start para empezar.")
        return
    await q.edit_message_reply_markup(None)
    await _paso(update, context, rd.Entrada(boton=q.data))
