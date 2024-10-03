import asyncio
from aiogram import exceptions
from aiogram import Bot, Dispatcher
from aiogram.methods import DeleteWebhook
from handlers import router
from handler_admin import router_admin_panel
import database as db

async def on_startup():
    await db.db_start()

async def main():
    try:
        bot = Bot(token='6971765827:AAGGYCGi7ouJ_0A5ZKwFX-VPbm5Cl_sSI68')
        dp = Dispatcher()
        dp.include_routers(router, router_admin_panel)
        dp.startup.register(on_startup)
        await bot(DeleteWebhook(drop_pending_updates=True))
        await dp.start_polling(bot)
    except exceptions.TelegramNetworkError as e:
        print(f"Network error: {e}")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt():
        print('Бот выключен')