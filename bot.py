import os
import nest_asyncio
nest_asyncio.apply()

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from flask import Flask
import threading

TOKEN = os.environ.get("TOKEN")

base_text = (
"Будь ласка, з метою захисту персональних даних надішліть електронною поштою на адресу "
"i.ponomarchuk@adigestore.it необхідну інформацію:\n\n"

"1. Cognome Nome\n"
"2. Indirizzo di residenza\n"
"3. Telefono italiano\n"
"4. WhatsApp\n"
"5. Stato della famiglia\n"
"6. Professione\n"
"7. Note\n\n"

"Долучіть необхідні документи:\n{docs}\n\n"

"Для пришвидшення обробки інформації зазначте тему звернення в назві листа."
)

docs_map = {
"AUTO": "Carta d'identità fronte/retro\nPatente fronte/retro\nLibretto fronte/retro\nCertificato Ucraino MTSBU",
"CASA": "Carta d'identità fronte/retro",
"SALUTE": "Carta d'identità fronte/retro",
"ALTRO": "Carta d'identità fronte/retro",
"VITA": "Carta d'identità fronte/retro",
"PENSIONE": "Carta d'identità fronte/retro",
"LUCE/GAS": "Carta d'identità fronte/retro\nBolletto LUCE\nBolletto GAS"
}

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚗 СТРАХУВАННЯ", callback_data="insurance")],
        [InlineKeyboardButton("🛡 ЗАХИСТ МАЙБУТНЬОГО", callback_data="future")],
        [InlineKeyboardButton("💡 ЕКОНОМІЯ LUCE/GAS", callback_data="energy")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Мене звуть Ірина Гертнер.\n"
        "Я вітаю Вас в офісі фінансових рішень для українців в Італії.\n"
        "Чим можу Вам допомогти?",
        reply_markup=main_menu()
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    if query.data == "insurance":

        kb = [[InlineKeyboardButton(x, callback_data=x)] for x in ["AUTO","CASA","SALUTE","ALTRO"]]
        kb.append([InlineKeyboardButton("⬅️ Назад", callback_data="back")])

        await query.edit_message_text("Оберіть вид страхування:", reply_markup=InlineKeyboardMarkup(kb))

    elif query.data == "future":

        kb = [[InlineKeyboardButton(x, callback_data=x)] for x in ["VITA","PENSIONE"]]
        kb.append([InlineKeyboardButton("⬅️ Назад", callback_data="back")])

        await query.edit_message_text("Оберіть програму:", reply_markup=InlineKeyboardMarkup(kb))

    elif query.data == "energy":

        kb = [[InlineKeyboardButton("LUCE/GAS", callback_data="LUCE/GAS")]]
        kb.append([InlineKeyboardButton("⬅️ Назад", callback_data="back")])

        await query.edit_message_text("Оберіть тему:", reply_markup=InlineKeyboardMarkup(kb))

    elif query.data == "back":

        await query.edit_message_text(
            "Чим можу Вам допомогти?",
            reply_markup=main_menu()
        )

    else:

        docs = docs_map.get(query.data, "")

        kb = [[InlineKeyboardButton("⬅️ Назад", callback_data="back")]]

        await query.edit_message_text(
            f"Тема: {query.data}\n\n" + base_text.format(docs=docs),
            reply_markup=InlineKeyboardMarkup(kb)
        )

async def auto_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Дякую за звернення. Після відправки листа я зв'яжусь із Вами телефоном "
        "для персональної консультації.\n\nІрина Гертнер"
    )

def run_bot():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_reply))

    app.run_polling()

# --- маленький сервер для Render ---

flask_app = Flask('')

@flask_app.route('/')
def home():
    return "Bot is alive"

def run():
    flask_app.run(host='0.0.0.0', port=10000)

threading.Thread(target=run).start()

run_bot()
