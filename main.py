import os
import json
from dotenv import load_dotenv
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, Filters

# Загрузка переменных окружения
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Путь к файлу с контактами
CONTACTS_FILE = "contacts.json"

# Инициализация данных
def load_contacts():
    try:
        with open(CONTACTS_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"users": []}

def save_contacts(data):
    with open(CONTACTS_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    button = KeyboardButton(text="Поделиться контактом", request_contact=True)
    markup = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[button]])

    await update.message.reply_text("Пожалуйста, поделись своим номером:", reply_markup=markup)

# Обработка контакта
async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    user_id = contact.user_id
    phone_number = contact.phone_number
    first_name = contact.first_name

    contacts = load_contacts()

    # Проверяем, нет ли дубликатов
    for user in contacts["users"]:
        if user["id"] == user_id:
            await update.message.reply_text("Вы уже зарегистрированы!")
            return

    # Добавляем нового пользователя
    new_user = {
        "id": user_id,
        "name": first_name,
        "phone": phone_number
    }
    contacts["users"].append(new_user)
    save_contacts(contacts)

    await update.message.reply_text("Спасибо! Ваш контакт сохранён.")

# Запуск бота
def main():
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(Filters.contact, handle_contact))

    application.run_polling()

if __name__ == '__main__':
    main()
