from aiogram import Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from database import Database

del_event = Router()
db = Database()

@del_event.message(Command("delete_events"))
async def delete_event(message: Message):
    user_id = message.from_user.id


    events = db.get_user_events(user_id)

    # Фильтруем события, чтобы исключить те, где есть значения None
    events = [event for event in events if event['name'] and event['description'] and event['time']]

    if not events:
        await message.answer("У вас пока нет сохранённых событий.")
        return

    # Создаём клавиатуру с кнопками для каждого события
    buttons = []
    for event in events:
        button_text = f"{event['date']} {event['time']} - {event['name']}"
        callback_data = f"delete_{event['date']}_{event['time']}"
        buttons.append(InlineKeyboardButton(text=button_text, callback_data=callback_data))


    if not buttons:
        await message.answer("У вас нет событий для удаления.")
        return


    markup = InlineKeyboardMarkup(inline_keyboard=[buttons])

    await message.answer("Выберите событие, которое хотите удалить:", reply_markup=markup)

@del_event.callback_query(lambda callback: callback.data.startswith("delete_"))
async def confirm_delete(callback: CallbackQuery):
    # Извлекаем дату и время события из callback_data
    _, event_date, event_time = callback.data.split("_")
    user_id = callback.from_user.id

    # Удаляем событие из базы данных
    db.delete_event(user_id=user_id, date=event_date, time=event_time)


    await callback.message.answer(f"Событие на {event_date} в {event_time} успешно удалено.")
    await callback.answer()
