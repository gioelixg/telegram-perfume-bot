import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, CallbackQueryHandler

# Configurazione
load_dotenv()
TOKEN = os.getenv('TOKEN')
GROUP_ID = os.getenv('GROUP_ID')
OFFERTE_FILE = 'offerte.json'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

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
        await context.bot.send_message(chat_id=GROUP_ID, text="🔍 Nuove offerte in arrivo a breve!")
        return

    messaggio = (
        f"🎉 **OFFERTA DEL GIORNO** 🎉\n\n"
        f"✨ {offerta['nome']}\n"
        f"💶 Prezzo: {offerta['prezzo']}\n"
        f"⏰ Valida fino al {offerta['scadenza']}\n\n"
        f"[🛒 Acquista ora]({offerta['link_affiliato']})"
    )

    keyboard = [[InlineKeyboardButton("Acquista", url=offerta['link_affiliato'])]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=GROUP_ID,
        text=messaggio,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text('Bot avviato! Usa /offerta per vedere la promozione corrente')

def main():
    application = Application.builder().token(TOKEN).build()

    # Comandi
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("offerta", lambda u,c: invia_offerta(c)))

    # Invio automatico giornaliero (alle 10:00)
    job_queue = application.job_queue
    job_queue.run_daily(invia_offerta, days=(0,1,2,3,4,5,6), time=datetime.time(hour=8,0,0, tzinfo=datetime.timezone.utc))

    application.run_polling()

if __name__ == '__main__':
    main()