"""Bot de Telegram de colonIA: `uv run python -m app.bot` (long polling, no necesita URL pública).

Flujo de alta: nota de voz o texto → ficha → ubicación → "Así queda" / "Corregir". Nada se publica sin "Así queda".
"""

import logging
import os

import httpx
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from app.bot import repartidor
from app.config import settings
from app.services import altas
from app.services import repartidor_dialogo as rd

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("colonia.bot")

# Dirección pública de la web para los links (no es secreto).
BASE_URL = os.environ.get("PUBLIC_BASE_URL", "").rstrip("/") or rd.api_base() or "http://localhost:8000"

MENU = ReplyKeyboardMarkup(
    [["Dar de alta mi negocio"], ["Actualizar mi negocio"], ["Quiero ser repartidor"], ["Verificar tianguis"]],
    resize_keyboard=True,
)
PEDIR_UBICACION = ReplyKeyboardMarkup(
    [[KeyboardButton("📍 Mandar mi ubicación", request_location=True)]],
    resize_keyboard=True,
    one_time_keyboard=True,
)
CONFIRMAR = InlineKeyboardMarkup(
    [[InlineKeyboardButton("✅ Así queda", callback_data="ok"), InlineKeyboardButton("✏️ Corregir", callback_data="corregir")]]
)


def registrar_alta(entrada: altas.AltaIn) -> altas.Alta:
    """Con COLONIA_API_URL el alta va a la plataforma desplegada (POST /api/altas); si no, se guarda en local."""
    base = rd.api_base()
    if not base:
        return altas.crear_alta(entrada)
    r = httpx.post(f"{base}/api/altas", json=entrada.model_dump(mode="json"), timeout=60)  # Render tarda en despertar
    r.raise_for_status()
    return altas.Alta.model_validate(r.json())


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.clear()
    await update.message.reply_text(
        "¡Hola! Soy colonIA 👋, la red viva de la economía de barrio.\n"
        "Te ayudo a que tus vecinas y vecinos te encuentren, gratis y sin llenar formularios.\n\n"
        "Mándame una nota de voz contando qué vendes, a cuánto, qué días y a qué hora abres, "
        "y cómo te pueden pagar.",
        reply_markup=MENU,
    )


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    texto = update.message.text
    if texto == "Quiero ser repartidor":
        await repartidor.iniciar(update, context)
    elif texto == "Verificar tianguis":
        await update.message.reply_text("Mándame la ubicación del tianguis y una foto, y lo marcamos como verificado hoy.")
    elif texto == "Actualizar mi negocio":
        await update.message.reply_text("Cuéntame por voz qué cambió (precios, horario, productos) y lo actualizo.")
    else:
        await update.message.reply_text(
            "Va. Mándame una nota de voz 🎙️ o escríbeme: qué vendes, precios, días, horario y formas de pago.",
            reply_markup=ReplyKeyboardRemove(),
        )


async def _procesar_texto(update: Update, context: ContextTypes.DEFAULT_TYPE, texto: str) -> None:
    await update.message.reply_text("Armando tu ficha… ⏳")
    ficha, grabada = altas.extraer_ficha(texto)
    context.user_data["ficha"] = ficha.model_dump()
    context.user_data["demo"] = grabada
    aviso = "\n\n(dato de ejemplo: sin conexión a la IA)" if grabada else ""
    if "lat" not in context.user_data:
        await update.message.reply_text(
            "Así entendí tu ficha:\n\n" + altas.ficha_texto(ficha) + aviso
            + "\n\nAhora mándame tu ubicación para ponerte en el mapa 📍",
            reply_markup=PEDIR_UBICACION,
        )
    else:
        await _mostrar_confirmacion(update, context)


async def _mostrar_confirmacion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    ficha = altas.Ficha.model_validate(context.user_data["ficha"])
    lugar = ""
    cercano = altas.tianguis_cercano(context.user_data["lat"], context.user_data["lng"])
    if cercano:
        lugar = f"\n📍 En: {cercano.get('nombre')}"
    await update.effective_message.reply_text(
        "Revisa tu ficha:\n\n" + altas.ficha_texto(ficha) + lugar + "\n\n¿Así queda?",
        reply_markup=CONFIRMAR,
    )


async def voz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if repartidor.activo(context):
        return await repartidor.voz(update, context)
    archivo = await (update.message.voice or update.message.audio).get_file()
    audio = bytes(await archivo.download_as_bytearray())
    texto, grabada = altas.transcribir(audio)
    await update.message.reply_text(f"🎙️ Escuché: “{texto}”" + (" (ejemplo grabado)" if grabada else ""))
    await _procesar_texto(update, context, texto)


async def texto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if repartidor.activo(context):
        return await repartidor.texto(update, context)
    await _procesar_texto(update, context, update.message.text)


async def ubicacion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    loc = update.message.location
    context.user_data["lat"], context.user_data["lng"] = loc.latitude, loc.longitude
    if "ficha" in context.user_data:
        await update.message.reply_text("¡Ubicación recibida! 📍", reply_markup=ReplyKeyboardRemove())
        await _mostrar_confirmacion(update, context)
    else:
        await update.message.reply_text("¡Ubicación recibida! Ahora cuéntame por voz qué vendes 🎙️")


async def foto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if repartidor.activo(context):
        return await repartidor.foto(update, context)
    await update.message.reply_text(
        "¡Bonita foto! 📸 Por ahora solo la guardo si tú me dices. Cuéntame por voz qué vendes para armar tu ficha."
    )


async def boton(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if repartidor.activo(context):
        return await repartidor.boton(update, context)
    q = update.callback_query
    await q.answer()
    if q.data == "corregir":
        await q.edit_message_reply_markup(None)
        await q.message.reply_text("Va, dime otra vez por voz o por texto cómo queda tu ficha.")
        return
    if "ficha" not in context.user_data or "lat" not in context.user_data:
        await q.message.reply_text("Me falta tu ficha o tu ubicación. Empieza con /start.")
        return
    alta = registrar_alta(altas.AltaIn(
        ficha=altas.Ficha.model_validate(context.user_data["ficha"]),
        lat=context.user_data["lat"],
        lng=context.user_data["lng"],
        origen="telegram",
        confirmado=True,
        demo_data=bool(context.user_data.get("demo")),
    ))
    log.info("alta %s h3=%s", alta.id, alta.h3)
    await q.edit_message_reply_markup(None)
    await q.message.reply_text(
        "🎉 ¡Listo! Ya eres parte de colonIA: apareces en el mapa de tu barrio y en las rutas de compra de tus vecinos.\n\n"
        f"Tu página: {BASE_URL}/n/{alta.slug}\n"
        f"Tu panel (privado): {BASE_URL}/#/negocio/{alta.id}",
        reply_markup=MENU,
    )
    context.user_data.clear()


def main() -> None:
    if not settings.telegram_bot_token:
        raise SystemExit("Falta TELEGRAM_BOT_TOKEN en .env. Para la demo sin Telegram: uv run python scripts/simular_alta.py")
    app = Application.builder().token(settings.telegram_bot_token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("^(Dar de alta mi negocio|Actualizar mi negocio|Quiero ser repartidor|Verificar tianguis)$"), menu))
    app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, voz))
    app.add_handler(MessageHandler(filters.LOCATION, ubicacion))
    app.add_handler(MessageHandler(filters.PHOTO, foto))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, texto))
    app.add_handler(CallbackQueryHandler(boton))
    log.info("Bot de colonIA escuchando (long polling)")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
