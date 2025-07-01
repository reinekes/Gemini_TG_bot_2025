import os
from telegram import Update, ReplyKeyboardMarkup, Document, Video
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler
from dotenv import load_dotenv
from google import genai
from google.genai import types
import requests
import httpx
import io

load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
    raise ValueError('Не найден TELEGRAM_TOKEN или GEMINI_API_KEY в .env')

client = genai.Client(api_key=GEMINI_API_KEY)

# Для хранения контекста диалога
user_context = {}

MENU_TEXT = (
    "Я — многофункциональный Gemini-бот!\n\n"
    "Доступные команды:\n"
    "/summarize — резюмировать текст\n"
    "/translate — перевод текста\n"
    "/code — генерация/объяснение кода\n"
    "/idea — генерация идей\n"
    "/story — креатив: стих, рассказ, шутка\n"
    "/image — анализ изображения (отправь фото или картинку)\n"
    "/pdf — анализ PDF-документа (отправь файл или ссылку)\n"
    "/video — анализ видео (отправь видеофайл или ссылку на YouTube)\n"
    "/reset — сбросить диалоговый контекст\n"
    "\nПросто напиши сообщение — я отвечу как умный ассистент!"
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text(MENU_TEXT)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text(MENU_TEXT)

async def summarize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or not update.message or context.user_data is None:
        return
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    await update.message.reply_text('Пришли мне текст, который нужно резюмировать.')
    context.user_data['mode'] = 'summarize'

async def translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or not update.message or context.user_data is None:
        return
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    await update.message.reply_text('Пришли мне текст для перевода (язык определю автоматически).')
    context.user_data['mode'] = 'translate'

async def code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or not update.message or context.user_data is None:
        return
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    await update.message.reply_text('Опиши задачу или пришли код — я помогу с генерацией или объяснением.')
    context.user_data['mode'] = 'code'

async def idea(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or not update.message or context.user_data is None:
        return
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    await update.message.reply_text('О чём нужна идея? (например: стартап, подарок, мероприятие)')
    context.user_data['mode'] = 'idea'

async def story(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or not update.message or context.user_data is None:
        return
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    await update.message.reply_text('Что сгенерировать? (стих, рассказ, шутку, сказку и т.д.)')
    context.user_data['mode'] = 'story'

async def image_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or not update.message or context.user_data is None:
        return
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    await update.message.reply_text('Отправь мне фото или картинку, и я опишу, что на ней изображено.')
    context.user_data['mode'] = 'image'

async def pdf_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or not update.message or context.user_data is None:
        return
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    await update.message.reply_text('Отправь мне PDF-файл или ссылку на PDF-документ, и я сделаю его резюме.')
    context.user_data['mode'] = 'pdf'

async def video_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or not update.message or context.user_data is None:
        return
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    await update.message.reply_text('Отправь мне видеофайл (mp4, mov и др., до 20 МБ) или ссылку на YouTube, и я сделаю его резюме.')
    context.user_data['mode'] = 'video'

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not update.message or context.user_data is None:
        return
    user_id = update.effective_user.id
    user_context.pop(user_id, None)
    context.user_data.clear()
    await update.message.reply_text('Контекст диалога сброшен!')

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.document:
        return
    document: Document = update.message.document
    if document.mime_type != 'application/pdf':
        await update.message.reply_text('Пожалуйста, отправь PDF-файл.')
        return
    chat_id = update.effective_chat.id if update.effective_chat else update.message.chat_id
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    file = await document.get_file()
    file_bytes = await file.download_as_bytearray()
    try:
        pdf_part = types.Part.from_bytes(data=bytes(file_bytes), mime_type='application/pdf')
        prompt = "Сделай краткое резюме этого PDF-документа."
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[pdf_part, prompt]
        )
        answer = response.text if response.text else 'Нет ответа от Gemini.'
    except Exception as e:
        answer = f'Ошибка анализа PDF: {e}'
    await update.message.reply_text(answer)

async def handle_pdf_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return False
    text = update.message.text.strip()
    if text.lower().endswith('.pdf') and (text.startswith('http://') or text.startswith('https://')):
        chat_id = update.effective_chat.id if update.effective_chat else update.message.chat_id
        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        try:
            pdf_bytes = httpx.get(text, timeout=30).content
            pdf_part = types.Part.from_bytes(data=pdf_bytes, mime_type='application/pdf')
            prompt = "Сделай краткое резюме этого PDF-документа."
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[pdf_part, prompt]
            )
            answer = response.text if response.text else 'Нет ответа от Gemini.'
        except Exception as e:
            answer = f'Ошибка анализа PDF по ссылке: {e}'
        await update.message.reply_text(answer)
        return True
    return False

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.video:
        return
    video: Video = update.message.video
    chat_id = update.effective_chat.id if update.effective_chat else update.message.chat_id
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    file = await video.get_file()
    video_bytes = await file.download_as_bytearray()
    try:
        video_part = types.Part.from_bytes(data=bytes(video_bytes), mime_type='video/mp4')
        prompt = "Сделай краткое резюме этого видео."
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[video_part, prompt]
        )
        answer = response.text if response.text else 'Нет ответа от Gemini.'
    except Exception as e:
        answer = f'Ошибка анализа видео: {e}'
    await update.message.reply_text(answer)

async def handle_youtube_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return False
    text = update.message.text.strip()
    if 'youtube.com/watch' in text or 'youtu.be/' in text:
        chat_id = update.effective_chat.id if update.effective_chat else update.message.chat_id
        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        try:
            video_part = types.Part(file_data=types.FileData(file_uri=text))
            prompt = "Сделай краткое резюме этого видео."
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[video_part, prompt]
            )
            answer = response.text if response.text else 'Нет ответа от Gemini.'
        except Exception as e:
            answer = f'Ошибка анализа YouTube-видео: {e}'
        await update.message.reply_text(answer)
        return True
    return False

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text or not update.effective_user or context.user_data is None:
        return
    # Проверяем, не PDF-ссылка или YouTube-ссылка ли это
    if context.user_data.get('mode') == 'pdf':
        if await handle_pdf_link(update, context):
            context.user_data.pop('mode', None)
            return
    if context.user_data.get('mode') == 'video':
        if await handle_youtube_link(update, context):
            context.user_data.pop('mode', None)
            return
    chat_id = update.effective_chat.id if update.effective_chat else update.message.chat_id
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    user_id = update.effective_user.id
    user_message = update.message.text
    mode = context.user_data.get('mode') if context.user_data else None
    prompt = ''
    if mode == 'summarize':
        prompt = f'Сделай краткое резюме следующего текста на русском языке:\n{user_message}'
        if context.user_data:
            context.user_data.pop('mode', None)
    elif mode == 'translate':
        prompt = f'Переведи на русский или английский язык (определи автоматически, какой нужен перевод):\n{user_message}'
        if context.user_data:
            context.user_data.pop('mode', None)
    elif mode == 'code':
        prompt = f'Помоги с кодом или объясни его. Запрос: {user_message}'
        if context.user_data:
            context.user_data.pop('mode', None)
    elif mode == 'idea':
        prompt = f'Сгенерируй креативные идеи по теме: {user_message}'
        if context.user_data:
            context.user_data.pop('mode', None)
    elif mode == 'story':
        prompt = f'Сгенерируй {user_message} на русском языке.'
        if context.user_data:
            context.user_data.pop('mode', None)
    elif mode == 'pdf':
        await update.message.reply_text('Пожалуйста, отправь PDF-файл или ссылку на PDF.')
        return
    elif mode == 'video':
        await update.message.reply_text('Пожалуйста, отправь видеофайл (mp4, mov и др., до 20 МБ) или ссылку на YouTube.')
        return
    else:
        # Диалоговый режим с контекстом
        history = user_context.get(user_id, [])
        history.append({'role': 'user', 'text': user_message})
        prompt = f'Веди диалог, учитывая предыдущие сообщения: {user_message}'
        user_context[user_id] = history[-10:]  # Храним последние 10 сообщений
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        answer = response.text if response.text else 'Нет ответа от Gemini.'
        # Добавляем ответ в контекст
        if mode is None:
            user_context[user_id].append({'role': 'assistant', 'text': answer})
    except Exception as e:
        answer = f'Ошибка Gemini API: {e}'
    await update.message.reply_text(answer)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.photo:
        return
    chat_id = update.effective_chat.id if update.effective_chat else update.message.chat_id
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    # Получаем наибольшее по размеру фото
    photo = update.message.photo[-1]
    photo_file = await photo.get_file()
    photo_bytes = await photo_file.download_as_bytearray()
    # Отправляем изображение в Gemini
    try:
        image_part = types.Part.from_bytes(data=bytes(photo_bytes), mime_type='image/jpeg')
        prompt = "Опиши, что изображено на этом фото."
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[image_part, prompt]
        )
        answer = response.text if response.text else 'Нет ответа от Gemini.'
    except Exception as e:
        answer = f'Ошибка анализа изображения: {e}'
    await update.message.reply_text(answer)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('summarize', summarize))
    app.add_handler(CommandHandler('translate', translate))
    app.add_handler(CommandHandler('code', code))
    app.add_handler(CommandHandler('idea', idea))
    app.add_handler(CommandHandler('story', story))
    app.add_handler(CommandHandler('image', image_command))
    app.add_handler(CommandHandler('pdf', pdf_command))
    app.add_handler(CommandHandler('video', video_command))
    app.add_handler(CommandHandler('reset', reset))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.Document.PDF, handle_document))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print('Бот запущен...')
    app.run_polling() 