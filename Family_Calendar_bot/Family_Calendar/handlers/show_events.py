from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from database import Database


get_event_router = Router()
db = Database()


@get_event_router.message(Command("show_events"))
async def show_events(message: Message):
    user_id = message.from_user.id


    events = db.get_user_events(user_id)

    if not events:
        await message.answer("У вас пока нет сохранённых событий.")
        return

    # Формируем сообщение со списком событий
    response = "Ваши события:\n"
    for event in events:
        response += (
            f"📅 Дата: {event['date']}\n"
            f"🕒 Время: {event['time']}\n"
            f"🔖 Название: {event['name']}\n"
            f"📝 Описание: {event['description']}\n\n"
        )
    await message.answer(response)