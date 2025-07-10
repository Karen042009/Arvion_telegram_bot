#!/home/8Khumaryan8/.virtualenvs/my-bot-venv/bin/python
# -*- coding: utf-8 -*-

import os
import logging

# --- ՍԿԻԶԲ։ Proxy-ի գլոբալ կարգավորում ---
# Սա պետք է լինի ամենաառաջին գործողությունը, մինչև ցանցային գրադարանների import-ը
# Սա կաշխատի և՛ aiogram-ի, և՛ google-generativeai-ի համար
if 'PYTHONANYWHERE_VERSION' in os.environ or os.environ.get('HOME', '').startswith('/home/'):
    # Նախնական լոգինգ՝ ստուգելու համար, որ այս բլոկն աշխատում է
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    logging.info("PythonAnywhere environment detected. Setting global HTTPS_PROXY.")
    proxy_url = "http://proxy.server:3128"
    os.environ['HTTPS_PROXY'] = proxy_url
    os.environ['HTTP_PROXY'] = proxy_url
# --- ԱՎԱՐՏ։ Proxy-ի գլոբալ կարգավորում ---


import asyncio
from pathlib import Path

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import TELEGRAM_TOKEN
from database.db_utils import init_db
from bot.middlewares.localization import Localization, get_all_translations
from bot.handlers import (
    common_handlers,
    settings_handlers,
    translate_handlers,
    learning_handlers,
    chat_handlers,
)

async def main():
    # Լոգինգի հիմնական կոնֆիգուրացիան՝ մանրամասն ֆորմատով
    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s - %(levelname)s - %(name)s - "
            "[%(filename)s:%(lineno)d] - %(message)s"
        ),
        force=True # force=True-ն թույլ է տալիս վերասահմանել նախնական կոնֆիգուրացիան
    )

    if not TELEGRAM_TOKEN:
        logging.critical("TELEGRAM_BOT_TOKEN not found in environment variables.")
        return

    await init_db()

    # Bot-ը ստեղծում ենք առանց session-ի, այն ինքը կօգտագործի համակարգային proxy-ն
    bot = Bot(
        token=TELEGRAM_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    locales_dir = Path(__file__).parent / "locales"
    loc_middleware = Localization(locales_dir=locales_dir)
    dp.update.middleware(loc_middleware)
    bot.loc_middleware = loc_middleware

    dp.include_router(common_handlers.common_router)
    dp.include_router(settings_handlers.settings_router)
    dp.include_router(translate_handlers.translate_router)
    dp.include_router(learning_handlers.learning_router)
    dp.include_router(chat_handlers.chat_router)

    # ------------------ Reply Keyboard Handlers ------------------
    all_translate_texts = get_all_translations("translate_button", loc_middleware.locales)
    @dp.message(F.text.in_(all_translate_texts))
    async def handle_translate_text(message, user_db, state):
        await translate_handlers.cb_enter_translator(message, user_db, state)

    all_learn_texts = get_all_translations("learn_button", loc_middleware.locales)
    @dp.message(F.text.in_(all_learn_texts))
    async def handle_learn_text(message, user_db, state):
        await learning_handlers.cb_main_menu_learn(message, user_db, state)

    all_chat_texts = get_all_translations("chat_button", loc_middleware.locales)
    @dp.message(F.text.in_(all_chat_texts))
    async def handle_chat_text(message, state):
        await chat_handlers.cb_chat_entry(message, state)

    all_settings_texts = get_all_translations("settings_button", loc_middleware.locales)
    @dp.message(F.text.in_(all_settings_texts))
    async def handle_settings_text(message, user_db, state):
        await settings_handlers.cb_main_menu_settings(message, user_db, state)
    # -----------------------------------------------------------

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as e:
        logging.critical(f"An error occurred during polling: {e}")
    finally:
        if bot.session:
            await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())