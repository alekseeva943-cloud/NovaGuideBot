
# =========================================
# FILE: texts.py
# PATH: /NovaGuideBot/texts.py
#
# ОТВЕЧАЕТ ЗА:
# - все UI тексты бота
# - мультиязычность
# - onboarding тексты
# =========================================

TEXTS = {

    # =====================================
    # RUSSIAN
    # =====================================

    "ru": {

        "welcome": """
Привет 👋

Я вижу, что в Telegram вас зовут:
{name}

Мне обращаться к вам так?
""",

        "enter_name": """
Введите имя,
которое хотите использовать 😊
""",

        "detected_language": """
Отлично 😊

Я вижу, что ваш Telegram язык:
{language}

Оставить его основным?
""",

        "enter_language": """
Напишите язык,
который хотите использовать 😊
""",

        "choose_style": """
Теперь выберите стиль общения 😊

Например:

- Кратко
- Подробно
- Профессионально
- Неформально
""",

        "profile_saved": """
Анкета сохранена ✅

Теперь можете задавать вопросы 😊
""",

        "fill_profile_first": """
Сначала заполните анкету 😊

Используйте:
/start
"""
    },

    # =====================================
    # ENGLISH
    # =====================================

    "en": {

        "welcome": """
Hello 👋

I see your Telegram name is:
{name}

Should I call you that?
""",

        "enter_name": """
Enter the name
you want to use 😊
""",

        "detected_language": """
Great 😊

I see your Telegram language is:
{language}

Keep it as your main language?
""",

        "enter_language": """
Type the language
you want to use 😊
""",

        "choose_style": """
Now choose your communication style 😊

Examples:

- Short
- Detailed
- Professional
- Friendly
""",

        "profile_saved": """
Profile saved ✅

Now you can ask questions 😊
""",

        "fill_profile_first": """
Please complete your profile first 😊

Use:
/start
"""
    }
}


# =========================================
# GET TEXT
# =========================================

def get_text(
    language_code: str,
    key: str,
    **kwargs
) -> str:

    language = language_code.lower()

    # FALLBACK
    if language not in TEXTS:

        language = "en"

    text = TEXTS[language].get(
        key,
        ""
    )

    return text.format(
        **kwargs
    )
