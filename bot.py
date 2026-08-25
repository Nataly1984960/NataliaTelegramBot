"""Простой Telegram-бот AI-помощника Натальи."""

import logging
import os

from dotenv import load_dotenv
from openai import OpenAI

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
        MessageHandler,
    filters,
)


# Загружаем BOT_TOKEN из файла .env в переменные окружения.
load_dotenv(override=True)

BOT_TOKEN = os.getenv("BOT_TOKEN")
YANDEX_API_KEY = os.getenv("YANDEX_API_KEY")
YANDEX_FOLDER_ID = os.getenv("YANDEX_FOLDER_ID")
client = OpenAI(
    api_key=YANDEX_API_KEY,
    base_url="https://ai.api.cloud.yandex.net/v1",
    project=YANDEX_FOLDER_ID,
)


WELCOME_MESSAGE = (
    "Добро пожаловать! 👋 Я AI-помощник Натальи. "
    "Выберите нужный раздел."
)

# Тексты кнопок и соответствующие тестовые ответы.
BUTTON_RESPONSES = {
    "about": (
    "👩 Обо мне\n\n"
    "Меня зовут Наталья. Я преподаватель английского языка и человек, "
    "который любит развиваться, пробовать новое и помогать другим двигаться вперёд.\n\n"
    "📚 Помогаю изучать английский понятно и без скучной зубрёжки.\n"
    "💻 Использую современные digital- и AI-инструменты в обучении.\n"
    "✨ Верю, что учиться новому можно в любом возрасте — главное найти свой формат "
    "и не бояться начинать.\n\n"
    "Здесь вы можете узнать обо мне больше, посмотреть отзывы, узнать свободное "
    "время для занятий или задать вопрос моему AI-помощнику."
),
    "reviews": (
    "⭐ Отзывы\n\n"
    "Здесь я собираю отзывы моих учеников.\n\n"
    "Для меня это не просто слова — это результаты, прогресс и та самая уверенность, "
    "которая появляется, когда английский постепенно перестаёт быть «страшным и непонятным» 😊\n\n"
    "Каждый ученик приходит со своей целью: кому-то нужен английский для учёбы, "
    "кому-то для путешествий, экзаменов или просто для себя.\n\n"
    "Скоро здесь появятся реальные отзывы и истории моих учеников ❤️"
),
    "availability": (
    "📅 Свободные окошки\n\n"
    "Здесь я публикую актуальное время для занятий.\n\n"
    "Сейчас свободны:\n"
    "Понедельник — 17:00\n"
    "Среда — 18:00\n"
    "Пятница — 16:00\n\n"
    "Если вам подходит одно из этих окошек — напишите мне, "
    "и мы договоримся о занятии.\n\n"
    "Расписание обновляется регулярно."
),
    "ask_ai": "Напишите свой вопрос. Скоро здесь будет отвечать AI-помощник.",
   "contact": "✉️ Связаться со мной\n\nНапишите мне в Telegram: @NatalyBolotina",
}


def build_menu() -> InlineKeyboardMarkup:
    """Создаёт меню разделов под приветственным сообщением."""
    keyboard = [
        [InlineKeyboardButton("👩 Обо мне", callback_data="about")],
        [InlineKeyboardButton("⭐ Отзывы", callback_data="reviews")],
        [
            InlineKeyboardButton(
                "📅 Свободные окошки", callback_data="availability"
            )
        ],
        [InlineKeyboardButton("🤖 Задать вопрос ИИ", callback_data="ask_ai")],
        [InlineKeyboardButton("✉️ Связаться со мной", callback_data="contact")],
    ]
    return InlineKeyboardMarkup(keyboard)

def build_back_button() -> InlineKeyboardMarkup:
    keyboard = [
    [InlineKeyboardButton("⬅️ Вернуться в меню", callback_data="back_to_menu")]
]
    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет приветствие и показывает меню при команде /start."""
    if update.message:
        await update.message.reply_text(
            WELCOME_MESSAGE,
            reply_markup=build_menu(),
        )


async def button_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Отправляет тестовый ответ после нажатия кнопки."""
    query = update.callback_query
    if query is None:
        return

    await query.answer()
    if query.data == "back_to_menu":
        await query.message.reply_text(
            WELCOME_MESSAGE,
            reply_markup=build_menu(),
        )
        return
    response = BUTTON_RESPONSES.get(query.data)
    if response:
               await query.message.reply_text(
            response,
            reply_markup=build_back_button(),
        )
async def handle_ai_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return

    user_text = update.message.text

    try:
        ai_response = client.chat.completions.create(
            model=f"gpt://{YANDEX_FOLDER_ID}/yandexgpt/latest",
            messages=[
               {
    "role": "system",
"content": (
    "Ты AI-помощник Натальи, преподавателя английского языка. "
    "Твоя задача — помогать ученикам изучать английский язык. "
    "Отвечай дружелюбно, понятно и не слишком длинно. "
    "Если ученик спрашивает правило грамматики — объясни его простыми словами и дай 2-3 примера. "
    "Если ученик спрашивает значение английского слова — дай перевод, простое объяснение и пример предложения. "
    "Если ученик просит практику — предложи небольшое упражнение из 3-5 заданий. "
    "Если ученик делает ошибку на английском — мягко исправь её и объясни почему. "
    "Учитывай уровень ученика, если он его указал. "
    "Не придумывай информацию о Наталье, стоимости занятий или расписании. "
    "По вопросам записи на занятия предложи воспользоваться разделом «Свободные окошки» или «Связаться со мной»."
),
            },
           {
            "role": "user",
            "content": user_text,
        
        },
        ])

        
            
            
            
        await update.message.reply_text(
                ai_response.choices[0].message.content,
                parse_mode="Markdown",
                reply_markup=build_back_button(),
            )

    except Exception as error:
       logging.exception("Ошибка YandexGPT: %s", error)
       await update.message.reply_text(
            "Не удалось получить ответ от AI. Попробуйте немного позже."
        )

def main() -> None:
    """Запускает бота в режиме long polling."""
    if not BOT_TOKEN:
        raise RuntimeError(
            "Не найден BOT_TOKEN. Добавьте токен в файл .env."
        )

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ai_message))

    application.run_polling()


if __name__ == "__main__":
    main()
