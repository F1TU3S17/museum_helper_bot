import asyncio
from aiogram import Bot, Dispatcher
from aiogram.methods import DeleteWebhook
from handlers import router
from handler_admin import router_admin_panel
import database as db
from config import Config, load_config

from environs import Env

env = Env()
env.read_env()

async def on_startup():
    await db.db_start()

async def main():

    config: Config = load_config()
    bot = Bot(token=config.tg_bot.token)
    dp = Dispatcher()

    dp.include_routers(router, router_admin_panel)
    dp.startup.register(on_startup)
    
    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot)



if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt():
        print('Бот выключен')