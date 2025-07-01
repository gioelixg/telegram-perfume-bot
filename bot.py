import os
import json
import logging
from datetime import time
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackContext,
    ApplicationBuilder,
)
from dotenv import load_dotenv

# Configurazione logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Caricamento variabili ambiente
load_dotenv()
TOKEN = os.getenv('TOKEN')
GROUP_ID = os.getenv('GROUP_ID')
OFFERTE_FILE = 'offerte.json'

def carica_offerte():
    with open(OFFERTE_FILE, 'r') as f:
        return json.load(f)

def offerta_attuale():
    offerte = carica_offerte()
    oggi = datetime.now().strftime("%Y-%m-%d")
    for offerta in offerte:
        if offerta['scadenza'] >= oggi:
            return offerta
    return None

async def invia_offerta(context: CallbackContext):
    offerta = offerta_attuale()
    if not offerta:
        await context.bot.send_message(
            chat_id=GROUP_ID,
            text="🔍 Nuove offerte in arrivo a breve!"
        )
        return

    messaggio = (
        f"🎉 **OFFERTA DEL GIORNO** 🎉\n\n"
        f"✨ {offerta['nome']}\n"
        f"💶 Prezzo: {offerta['prezzo']}\n"
        f"⏰ Valida fino al {offerta['scadenza']}\n\n"
        f"[🛒 Acquista ora]({offerta['link_affiliato']})"
    )

    await context.bot.send_message(
        chat_id=GROUP_ID,
        text=messaggio,
        parse_mode='Markdown'
    )

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text('Bot avviato! Usa /offerta per vedere la promozione corrente')

async def post_init(app: Application):
    """Configurazione post-inizializzazione"""
    app.job_queue.scheduler.configure(timezone='UTC')

def main():
    application = (
        ApplicationBuilder()
        .token(TOKEN)
        .post_init(post_init)  # Corretto: ora è una coroutine
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("offerta", lambda u,c: invia_offerta(c)))

    job_queue = application.job_queue
    job_queue.run_daily(
        invia_offerta,
        time=time(hour=8),  # 08:00 UTC
        days=(0, 1, 2, 3, 4, 5, 6),
        name="invia_offerta_giornaliera"
    )

    application.run_polling()

if __name__ == '__main__':
    main()