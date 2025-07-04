# Gemini Telegram Bot

Многофункциональный Telegram-бот на Python с интеграцией Google Gemini API.

## Возможности
- Вопрос-ответ через Gemini 2.5 Flash
- Резюмирование текста
- Перевод текста
- Генерация и объяснение кода
- Генерация идей
- Креатив: стихи, рассказы, шутки
- Диалоговый режим с контекстом
- Сброс контекста
- **Анализ изображений**: описание, визуальные вопросы и ответы (отправь фото или используй /image)
- **Анализ PDF-документов**: резюме, ответы на вопросы, работа с файлами и ссылками (отправь PDF или используй /pdf)
- **Анализ видео**: резюме, ответы на вопросы, поддержка видеофайлов и YouTube (отправь видео или используй /video)
- **Анализ аудио**: резюме, транскрипция, ответы на вопросы (отправь аудиофайл или используй /audio)
- Хранение ключей в .env

## Установка

1. Установите Python 3.10 с официального сайта: https://www.python.org/downloads/release/python-31011/
2. Клонируйте репозиторий:
   ```
   git clone https://github.com/reinekes/Gemini_TG_bot_2025.git
   ```
3. Перейдите в папку проекта:
   ```
   cd Gemini_TG_bot_2025
   ```
4. Создайте и активируйте виртуальное окружение:
   ```
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
5. Установите зависимости:
   ```
   pip install -r requirements.txt
   ```
6. Создайте файл `.env` и добавьте ваши ключи:
   ```
   TELEGRAM_TOKEN=ваш_токен
   GEMINI_API_KEY=ваш_ключ
   ```

## Запуск

```bash
python bot.py
```

## Использование
- Просто напишите сообщение — бот ответит как ассистент.
- Используйте команды:
  - `/summarize` — резюмировать текст
  - `/translate` — перевод текста
  - `/code` — генерация/объяснение кода
  - `/idea` — генерация идей
  - `/story` — креатив (стих, рассказ, шутка)
  - `/image` — анализ изображения (отправьте фото после команды)
  - `/pdf` — анализ PDF (отправьте PDF-файл или ссылку)
  - `/video` — анализ видео (отправьте видеофайл или ссылку на YouTube)
  - `/audio` — анализ аудио (отправьте аудиофайл)
  - `/reset` — сбросить диалоговый контекст
- Можно просто отправить фото, PDF, видео или аудио — бот опишет, что на нём изображено, сделает резюме документа, видео или аудиофайла.

## Важно
- Для работы Gemini API необходим VPN с выходом в поддерживаемую страну (например, Германия, США, Польша и др.).
- Если бот не отвечает — проверьте доступность Telegram и Google Gemini через ваш VPN. 