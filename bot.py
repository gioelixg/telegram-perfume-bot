import os
import json
import logging
from datetime import datetime, time
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackContext
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
    try:
        with open(OFFERTE_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def offerta_attuale():
    offerte = carica_offerte()
    oggi = datetime.now().strftime("%Y-%m-%d")
    for offerta in offerte:
        if offerta['scadenza'] >= oggi:
            return offerta
    return None

async def invia_offerta(context: CallbackContext):
    try:
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
        logger.info("Offerta inviata correttamente")
    except Exception as e:
        logger.error(f"Errore nell'invio offerta: {str(e)}")

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text('✅ Bot avviato! Usa /offerta per vedere la promozione corrente')

async def manual_offerta(update: Update, context: CallbackContext):
    await invia_offerta(context)
    await update.message.reply_text('📬 Offerta inviata manualmente!')

def main():
    # Costruisci l'applicazione - VERSIONE SEMPLIFICATA
    application = Application.builder().token(TOKEN).build()
    
    # Aggiungi gestori di comandi
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("offerta", manual_offerta))
    
    # Configura il job giornaliero - APPROCCIO ALTERNATIVO
    job_queue = application.job_queue
    job_queue.run_repeating(
        invia_offerta,
        interval=86400,  # 24 ore in secondi
        first=10,  # Invia dopo 10 secondi dall'avvio (per test)
        name="daily_offer_job"
    )
    
    # Avvia il bot
    application.run_polling()

if __name__ == '__main__':
    main()