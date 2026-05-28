# =========================================
# FILE: handlers.py
# PATH: /NovaGuideBot/handlers.py
#
# ОТВЕЧАЕТ ЗА:
# - onboarding flow
# - callbacks
# - profile view/edit
# - AI chat
# - typing animation
# =========================================

from telegram import Update

from telegram.constants import ChatAction

from telegram.ext import (
    ContextTypes
)

from database import (
    get_user,
    save_user
)

from ai_service import (
    generate_answer
)

from keyboards import (
    main_keyboard,
    name_keyboard,
    language_keyboard
)

from texts import (
    get_text
)


# =========================================
# START
# =========================================

async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user

    if not user:
        return

    if not update.message:
        return

    context.user_data.clear()

    telegram_name = user.first_name

    context.user_data["telegram_name"] = (
        telegram_name
    )

    await update.message.reply_text(

        get_text(
            "ru",
            "welcome",
            name=telegram_name
        ),

        reply_markup=name_keyboard
    )


# =========================================
# CALLBACKS
# =========================================

async def callbacks_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    if not query:
        return

    if not query.message:
        return

    await query.answer()

    # =====================================
    # KEEP NAME
    # =====================================

    if query.data == "keep_name":

        telegram_name = context.user_data.get(
            "telegram_name"
        )

        context.user_data["name"] = (
            telegram_name
        )

        await query.message.reply_text(

            get_text(
                "ru",
                "choose_style"
            )
        )

        context.user_data["step"] = (
            "waiting_style"
        )

        return

    # =====================================
    # CHANGE NAME
    # =====================================

    if query.data == "change_name":

        context.user_data["step"] = (
            "waiting_name"
        )

        await query.message.reply_text(

            get_text(
                "ru",
                "enter_name"
            )
        )

        return

    # =====================================
    # KEEP LANGUAGE (НОВЫЙ КОЛБЭК)
    # =====================================

    if query.data == "keep_language":
        # Пользователь оставил системный язык
        user = update.effective_user
        context.user_data["language"] = context.user_data.get("detected_language", "Русский")
        
        save_user(
            telegram_id=user.id,
            name=context.user_data.get("name", "Пользователь"),
            language=context.user_data["language"],
            style=context.user_data.get("style", "Обычный")
        )
        
        await query.message.reply_text(
            get_text("ru", "profile_saved"),
            reply_markup=main_keyboard
        )
        
        context.user_data.clear()
        return

    # =====================================
    # CHANGE LANGUAGE (существующая кнопка, НОВАЯ ЛОГИКА)
    # =====================================

    if query.data == "change_language":
        # Пользователь хочет изменить язык
        context.user_data["step"] = "waiting_language"
        
        await query.message.reply_text(
            get_text("ru", "enter_language")
        )
        return


# =========================================
# TEXT HANDLER
# =========================================

async def text_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

    user = update.effective_user

    if not user:
        return

    text = update.message.text

    # =====================================
    # ⚡ ОБРАБОТКА КОМАНДЫ /start (на случай, если CommandHandler не сработал)
    # =====================================

    if text == "/start":
        await start_command(update, context)
        return

    # =====================================
    # ПОЛУЧАЕМ ТЕКУЩИЙ ШАГ ОНБОРДИНГА
    # =====================================

    step = context.user_data.get(
        "step"
    )

    # =====================================
    # PROFILE BUTTON
    # =====================================

    if text == "👤 Моя анкета":

        db_user = get_user(
            user.id
        )

        if not db_user:

            await update.message.reply_text(
                """
Анкета не найдена 😢

Используйте:
/start
"""
            )

            return

        await update.message.reply_text(
            f"""
👤 Ваша анкета

Имя:
{db_user["name"]}

Стиль общения:
{db_user["style"]}

Язык:
{db_user["language"]}
"""
        )

        return

    # =====================================
    # WAITING NAME
    # =====================================

    if step == "waiting_name":

        context.user_data["name"] = (
            text
        )

        await update.message.reply_text(

            get_text(
                "ru",
                "choose_style"
            )
        )

        context.user_data["step"] = (
            "waiting_style"
        )

        return

    # =====================================
    # WAITING STYLE
    # =====================================

    if step == "waiting_style":

        context.user_data["style"] = (
            text
        )

        # =================================
        # НОВАЯ ЛОГИКА: СНАЧАЛА ДЕТЕКЦИЯ ЯЗЫКА
        # =================================
        
        # Определяем системный язык пользователя
        detected_language = "Русский"  # по умолчанию
        
        # Пробуем получить язык из user.language_code
        if user and user.language_code:
            lang_code = user.language_code.lower()
            if lang_code.startswith("ru"):
                detected_language = "Русский"
            elif lang_code.startswith("en"):
                detected_language = "English"
            elif lang_code.startswith("es"):
                detected_language = "Español"
            elif lang_code.startswith("de"):
                detected_language = "Deutsch"
            elif lang_code.startswith("fr"):
                detected_language = "Français"
            elif lang_code.startswith("zh"):
                detected_language = "中文"
            # Добавь другие языки при необходимости
        
        # Сохраняем детектированный язык в context.user_data
        context.user_data["detected_language"] = detected_language
        
        # Отправляем сообщение с выбором языка (как на скриншоте)
        await update.message.reply_text(
            f"Отлично 😊\n\nЯ вижу, что ваш системный язык: {detected_language}\n\nОставить его основным?",
            reply_markup=language_keyboard  # Используем твою существующую клавиатуру
        )
        
        # НЕ переходим к waiting_language — ждём выбора кнопки
        # context.user_data["step"] = "waiting_language" — убираем это!
        
        return

    # =====================================
    # WAITING LANGUAGE
    # =====================================

    if step == "waiting_language":

        context.user_data["language"] = (
            text
        )

        save_user(

            telegram_id=user.id,

            name=context.user_data.get(
                "name",
                "Пользователь"
            ),

            language=context.user_data.get(
                "language",
                "Русский"
            ),

            style=context.user_data.get(
                "style",
                "Обычный"
            )
        )

        await update.message.reply_text(

            get_text(
                "ru",
                "profile_saved"
            ),

            reply_markup=main_keyboard
        )

        context.user_data.clear()

        return

    # =====================================
    # AI CHAT (основная логика)
    # =====================================

    db_user = get_user(
        user.id
    )

    if not db_user:

        await update.message.reply_text(

            get_text(
                "ru",
                "fill_profile_first"
            )
        )

        return

    # =====================================
    # TYPING ANIMATION
    # =====================================

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.TYPING
    )

    answer = await generate_answer(

        question=text,

        user_name=db_user["name"],

        user_language=db_user["language"],

        user_style=db_user["style"]
    )

    await update.message.reply_text(
        answer
    )