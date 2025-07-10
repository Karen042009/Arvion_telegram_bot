import asyncio
import os
from dotenv import load_dotenv

# .env ֆայլից տվյալների բեռնում
load_dotenv('Arvion_Lingua_AI/.env') # Համոզվեք, որ ճանապարհը ճիշտ է ձեր կառուցվածքի համար

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# ԿԱՐԵՎՈՐ: Փոխարինեք 8Khumaryan8-ը ձեր PythonAnywhere-ի username-ով
WEBHOOK_HOST = "https://8Khumaryan8.pythonanywhere.com"
WEBHOOK_PATH = f"/{TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

async def set_hook():
    # Սա պարզ, առանց բարդ տրամաբանության սկրիպտ է
    from aiogram import Bot

    bot = Bot(token=TOKEN)
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(url=WEBHOOK_URL)
    print(f"Webhook has been set to {WEBHOOK_URL}")
    await bot.session.close()

if __name__ == "__main__":
    if not TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not found. Make sure your .env file is correct.")
    else:
        asyncio.run(set_hook())