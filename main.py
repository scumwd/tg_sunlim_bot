import asyncio
from aiogram import Bot, Dispatcher

from config import TOKEN
from app.database.models import async_main

bot = Bot(token=TOKEN)

async def main():
    from app.user import userRouter
    from app.admin import adminRouter

    dp = Dispatcher()
    dp.include_router(userRouter)
    dp.include_router(adminRouter)
    dp.startup.register(on_startup)
    await dp.start_polling(bot)

async def on_startup(dispatcher):
    await async_main()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
