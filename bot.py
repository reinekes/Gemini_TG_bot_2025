import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv
from google import genai

load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
    raise ValueError('Не найден TELEGRAM_TOKEN или GEMINI_API_KEY в .env')

client = genai.Client(api_key=GEMINI_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text('Привет! Задай мне любой вопрос.')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    user_message = update.message.text
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_message
        )
        answer = response.text if response.text else 'Нет ответа от Gemini.'
    except Exception as e:
        answer = f'Ошибка Gemini API: {e}'
    await update.message.reply_text(answer)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print('Бот запущен...')
    app.run_polling() 