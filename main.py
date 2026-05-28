
# =========================================
# FILE: main.py
# PATH: /NovaGuideBot/main.py
#
# ОТВЕЧАЕТ ЗА:
# - запуск Telegram-бота
# - регистрацию handlers
# - polling loop
# =========================================

import logging
import os

from dotenv import load_dotenv

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

from database import (
    init_db
)

from handlers import (
    start_command,
    callbacks_handler,
    text_handler
)


# =========================================
# ENV
# =========================================

load_dotenv()

BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN"
)

if not BOT_TOKEN:

    raise ValueError(
        "TELEGRAM_BOT_TOKEN не найден"
    )


# =========================================
# LOGGING
# =========================================

logging.basicConfig(
    level=logging.INFO
)


# =========================================
# MAIN
# =========================================

def main():

    # ИНИЦИАЛИЗАЦИЯ SQLITE
    init_db()

    # СОЗДАНИЕ BOT APP
    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    # =====================================
    # HANDLERS
    # =====================================

    app.add_handler(
        CommandHandler(
            "start",
            start_command
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            callbacks_handler
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            text_handler
        )
    )

    print("NovaGuideBot запущен 🚀")

    # START POLLING
    app.run_polling()


# =========================================
# ENTRYPOINT
# =========================================

if __name__ == "__main__":

    main()
