import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from config import (
    BOT_TOKEN, WEBHOOK_PATH, WEBHOOK_URL, WEB_SERVER_PORT
)
from database import init_db
from handlers import user, admin, callbacks

logging.basicConfig(level=logging.INFO)

async def on_startup(bot: Bot):
    await bot.set_webhook(WEBHOOK_URL)
    print(f"Вебхук установлен на {WEBHOOK_URL}")

def main():
    # Инициализация базы данных
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init_db())

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(admin.router)
    dp.include_router(user.router)
    dp.include_router(callbacks.router)

    app = web.Application()

    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot
    )
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    
    print(f"Сервер запускается на порту {WEB_SERVER_PORT}...")
    web.run_app(app, host="0.0.0.0", port=WEB_SERVER_PORT)

if __name__ == "__main__":
    main()