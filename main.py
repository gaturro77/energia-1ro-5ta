import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters
from groq import Groq
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_KEY = os.getenv("GROQ_API_KEY")

if not TELEGRAM_TOKEN or not GROQ_KEY:
    logger.error("Faltan TELEGRAM_BOT_TOKEN o GROQ_API_KEY en variables de entorno.")
    raise SystemExit("Pone las keys en .env (local) o en Render (ENV vars).")

groq_client = Groq(api_key=GROQ_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hola thiago. ¿Qué tema de energia veremos hoy? 😉")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = (update.message.text or "").strip()
    logger.info("Mensaje recibido: %s", user_msg)

    if user_msg == "":
        await update.message.reply_text("No te escuché, escribí algo.")
        return

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Sos un bot amable y conciso."},
                {"role": "user", "content": user_msg}
            ],
            max_tokens=512
        )
        bot_reply = response.choices[0].message["content"]
        await update.message.reply_text(bot_reply)
    except Exception as e:
        logger.exception("Error llamando a Groq")
        await update.message.reply_text("Perdón, hubo un error procesando tu mensaje.")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()