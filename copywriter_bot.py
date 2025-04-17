import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)
import openai  # Only needed if using OpenAI API

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
OPENAI_API_KEY = 'YOUR_OPENAI_API_KEY'  # Optional, only for AI generation

# Conversation states
SELECTING_ACTION, WRITING_BRIEF, GENERATING_TEXT, REVIEWING = range(4)

# Initialize OpenAI (if using)
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

def start(update: Update, context: CallbackContext) -> int:
    """Start the conversation and ask user what they want to do."""
    reply_keyboard = [['Создать пост', 'Написать отзыв', 'Копирайтинг']]
    
    update.message.reply_text(
        "Привет! Я бот-копирайтер. Чем могу помочь?\n\n"
        "Выберите действие:",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    
    return SELECTING_ACTION

def select_action(update: Update, context: CallbackContext) -> int:
    """Store the selected action and ask for details."""
    user_choice = update.message.text
    context.user_data['choice'] = user_choice
    
    if user_choice == 'Создать пост':
        update.message.reply_text(
            "Отлично! Давайте создадим пост.\n\n"
            "Опишите кратко, о чем должен быть пост, целевую аудиторию и стиль написания.\n\n"
            "Например: 'Нужен пост для Instagram о новом фитнес-клубе, целевая аудитория - женщины 25-40 лет, стиль - мотивирующий и дружелюбный'",
            reply_markup=ReplyKeyboardRemove(),
        )
    elif user_choice == 'Написать отзыв':
        update.message.reply_text(
            "Хорошо, помогу с отзывом.\n\n"
            "Опишите продукт/услугу, ваши впечатления и какой тон должен быть у отзыва (положительный, нейтральный, с критикой и т.д.).\n\n"
            "Например: 'Нужен отзыв на новый iPhone, впечатления положительные, но с небольшими замечаниями по батарее'",
            reply_markup=ReplyKeyboardRemove(),
        )
    elif user_choice == 'Копирайтинг':
        update.message.reply_text(
            "Копирайтинг - отличный выбор!\n\n"
            "Опишите задачу: что нужно написать (рекламный текст, описание товара, email-рассылку и т.д.), "
            "ключевые преимущества и целевую аудиторию.\n\n"
            "Например: 'Нужен текст для лендинга курса по Python, основные преимущества - практика и помощь с трудоустройством, ЦА - новички в IT'",
            reply_markup=ReplyKeyboardRemove(),
        )
    
    return WRITING_BRIEF

def receive_brief(update: Update, context: CallbackContext) -> int:
    """Receive the user's brief and generate or ask for more info."""
    brief = update.message.text
    context.user_data['brief'] = brief
    
    # Here you would typically process the brief and generate content
    # For this example, we'll simulate generation
    
    update.message.reply_text(
        "Спасибо за информацию! Генерирую текст...\n\n"
        "Это может занять несколько секунд."
    )
    
    # Simulate generation delay
    context.job_queue.run_once(generate_text, 3, context=update.message.chat_id)
    
    return GENERATING_TEXT

def generate_text(context: CallbackContext):
    """Generate text based on the brief (simulated or using AI)."""
    job = context.job
    chat_id = job.context
    
    # In a real bot, you would use AI or templates here
    # This is a simplified example
    
    # Example of using OpenAI API (uncomment if you have API key)
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional copywriter."},
                {"role": "user", "content": context.user_data['brief']}
            ]
        )
        generated_text = response.choices[0].message.content
    except Exception as e:
        generated_text = f"Извините, произошла ошибка при генерации текста: {str(e)}"
    """
    
    # Fallback text if not using AI
    choice = context.user_data.get('choice', 'Создать пост')
    brief = context.user_data.get('brief', '')
    
    if choice == 'Создать пост':
        generated_text = f"""📢 Новый пост по вашему запросу:

{brief}

🔹 Вот пример текста для поста:

"Друзья, у нас потрясающие новости! 🎉

Мы открываем двери нового фитнес-клуба [Название] в самом сердце города! 💪

✨ Просторные залы с современным оборудованием
✨ Профессиональные тренеры с индивидуальным подходом
✨ Зоны для функционального тренинга, йоги и кроссфита
✨ Удобное расположение и приятная атмосфера

Специально для новых клиентов - скидка 30% на первый месяц! 

Записывайтесь прямо сейчас и сделайте первый шаг к своей лучшей версии! 🚀

#фитнес #здоровье #спорт #тренировки #[город]"""
    elif choice == 'Написать отзыв':
        generated_text = f"""📝 Отзыв по вашему запросу:

{brief}

🔹 Вот пример отзыва:

"Пользуюсь новым iPhone уже две недели и хочу поделиться впечатлениями.

👍 Плюсы:
- Потрясающий экран с яркими цветами
- Молниеносная работа системы
- Отличная камера, особенно ночные снимки
- Приятный дизайн и удобный размер

👎 Минусы:
- Батарея могла бы быть лучше при активном использовании
- Быстро нагревается при играх или длительной съемке

В целом - отличный телефон, но есть небольшие недочеты. Рекомендую, если вы готовы к некоторым компромиссам."
"""
    else:  # Копирайтинг
        generated_text = f"""✍️ Рекламный текст по вашему запросу:

{brief}

🔹 Вот пример текста:

"Хотите освоить Python и начать карьеру в IT? 🐍

Наш курс Python Pro - это:

✅ Практика с первого занятия
✅ Реальные проекты в портфолио
✅ Поддержка менторов 24/7
✅ Гарантия трудоустройства или возврат денег

За 3 месяца вы:
- Научитесь писать чистый и эффективный код
- Освоите популярные фреймворки
- Разработаете 5 реальных проектов
- Подготовитесь к собеседованиям

Не упустите шанс изменить свою жизнь! Записывайтесь на бесплатный пробный урок по ссылке ниже.

#Python #Программирование #IT #Курсы #Карьера"
"""
    
    context.bot.send_message(chat_id=chat_id, text=generated_text)
    context.bot.send_message(
        chat_id=chat_id,
        text="Как вам результат? Могу внести правки или сгенерировать другой вариант.",
        reply_markup=ReplyKeyboardMarkup(
            [['Нравится', 'Сгенерировать другой'], ['Внести правки']],
            one_time_keyboard=True,
            resize_keyboard=True
        )
    )

def review_text(update: Update, context: CallbackContext) -> int:
    """Let the user review the generated text."""
    feedback = update.message.text
    
    if feedback == 'Нравится':
        update.message.reply_text(
            "Отлично! Рад, что вам понравилось. Если понадобится еще помощь - просто напишите /start",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    elif feedback == 'Сгенерировать другой':
        update.message.reply_text(
            "Генерирую другой вариант...",
            reply_markup=ReplyKeyboardRemove()
        )
        context.job_queue.run_once(generate_text, 3, context=update.message.chat_id)
        return GENERATING_TEXT
    else:  # Внести правки
        update.message.reply_text(
            "Опишите, какие правки нужно внести: какие части изменить, что добавить или убрать.",
            reply_markup=ReplyKeyboardRemove()
        )
        return REVIEWING

def apply_edits(update: Update, context: CallbackContext) -> int:
    """Apply user's edits to the text."""
    edits = update.message.text
    context.user_data['edits'] = edits
    
    update.message.reply_text(
        "Учитываю ваши правки и создаю новый вариант...",
        reply_markup=ReplyKeyboardRemove()
    )
    
    # Here you would typically regenerate with edits
    # For simplicity, we'll just show the same text with a note
    context.job_queue.run_once(
        lambda ctx: ctx.bot.send_message(
            chat_id=ctx.job.context,
            text=f"Вот текст с учетом ваших правок:\n\n{context.user_data.get('brief', '')}\n\n(Здесь был бы текст с изменениями: {edits})"
        ),
        3,
        context=update.message.chat_id
    )
    
    return review_text(update, context)

def cancel(update: Update, context: CallbackContext) -> int:
    """Cancel the conversation."""
    update.message.reply_text(
        'Хорошо, если понадобится помощь - просто напишите /start',
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler with the states
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECTING_ACTION: [
                MessageHandler(
                    Filters.regex('^(Создать пост|Написать отзыв|Копирайтинг)$'), select_action
                )
            ],
            WRITING_BRIEF: [
                MessageHandler(Filters.text & ~Filters.command, receive_brief)
            ],
            GENERATING_TEXT: [
                MessageHandler(
                    Filters.regex('^(Нравится|Сгенерировать другой|Внести правки)$'), review_text
                )
            ],
            REVIEWING: [
                MessageHandler(Filters.text & ~Filters.command, apply_edits)
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
