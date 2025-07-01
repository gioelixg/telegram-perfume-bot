import os
import json
import logging
from datetime import time, datetime, timedelta  # Import corretti
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackContext,
    CallbackQueryHandler,
    ApplicationBuilder  # Aggiunto per compatibilità
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

def main():
    # Configurazione application con post_init
    application = (
        ApplicationBuilder()
        .token(TOKEN)
        .post_init(lambda app: app.job_queue.scheduler.configure(timezone='UTC'))
        .build()
    )

    # Aggiunta handler
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("offerta", lambda u,c: invia_offerta(c)))

    # Configurazione job giornaliero
    job_queue = application.job_queue
    ora_invio = time(hour=8)  # 08:00 UTC
    job_queue.run_daily(
        invia_offerta,
        time=ora_invio,
        days=(0, 1, 2, 3, 4, 5, 6)  # Tutti i giorni
    )

    application.run_polling()

if __name__ == '__main__':
    main()