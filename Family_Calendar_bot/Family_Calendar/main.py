from aiogram import Bot, Dispatcher
import asyncio

from token_bot import Token
from handlers import exapmle, start, calendar, message_user, show_events, delete_event, help, notification


async def main():
    bot = Bot(token=Token)
    dp = Dispatcher()

    dp.include_router(start.start_router)
    dp.include_router(exapmle.example_router)
    dp.include_router(calendar.calendar_router)
    dp.include_router(message_user.message_router)
    dp.include_router(show_events.get_event_router)
    dp.include_router(delete_event.del_event)
    dp.include_router(help.help_router)
    dp.include_router(notification.notif_router)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        print("Бот запущен. Ожидание сообщений...")
        await dp.start_polling(bot)
    except Exception as e:
        print(f"Ошибка при запуске бота: {e}")
    finally:
        await bot.session.close()
        print("Бот завершил работу.")


if __name__ == "__main__":
    asyncio.run(main())
