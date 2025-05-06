from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton, CallbackQuery, Message
from aiogram.filters import Command
from datetime import datetime, timedelta
from database import Database
from aiogram.utils.keyboard import InlineKeyboardBuilder
from keyboards import comfirm_notif

calendar_router = Router()
db = Database()


class WaitEvent(StatesGroup):
    waiting_event_name = State()
    waiting_event_description = State()
    waiting_event_time = State()


def create_calendar(year: int = None, month: int = None):
    if year is None or month is None:
        now = datetime.now()
        year = now.year
        month = now.month

    builder = InlineKeyboardBuilder()  # Используем InlineKeyboardBuilder

    # Заголовок с названием месяца и года
    builder.row(InlineKeyboardButton(
        text=f"{datetime(year, month, 1).strftime('%B %Y')}",
        callback_data="ignore"
    ))

    # Дни недели
    days_of_week = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
    builder.row(*[InlineKeyboardButton(text=day, callback_data="ignore") for day in days_of_week])

    # Получаем события для выбранного месяца
    events = db.get_events_by_month(year, month)

    # Формируем список дней месяца
    first_day = datetime(year, month, 1)
    last_day = datetime(year, month + 1, 1) - timedelta(days=1) if month < 12 else datetime(year + 1, 1, 1) - timedelta(days=1)
    days_in_month = [i for i in range(1, last_day.day + 1)]

    # Создаем набор дат с событиями для быстрого поиска
    event_dates = {event['date'] for event in events}

    # Отступы для первого дня месяца
    offset = first_day.weekday()  # Понедельник - 0, ..., Воскресенье - 6
    days = []

    # Добавляем пустые кнопки для смещения
    for _ in range(offset):
        days.append(InlineKeyboardButton(text=" ", callback_data="ignore"))

    for day in days_in_month:
        date_str = f"{year}-{month:02d}-{day:02d}"
        emoji = "📅" if date_str in event_dates else ""
        days.append(InlineKeyboardButton(
            text=f"{day} {emoji}",
            callback_data=f"day_{date_str}"
        ))

    # Разбиваем дни на недели и добавляем их в разметку
    for i in range(0, len(days), 7):
        builder.row(*days[i:i + 7])

    # Кнопки для навигации по месяцам
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    builder.row(
        InlineKeyboardButton(text="<<", callback_data=f"prev_{prev_year}_{prev_month}"),
        InlineKeyboardButton(text=">>", callback_data=f"next_{next_year}_{next_month}")
    )

    return builder.as_markup()  # Преобразуем в InlineKeyboardMarkup


@calendar_router.message(Command("calendar"))
async def start(message: types.Message):
    """
    Отправляет календарь по команде /calendar.
    """
    await message.answer("Выберите дату:", reply_markup=create_calendar())


@calendar_router.callback_query(F.data.startswith("day_"))
async def process_day(callback_query: CallbackQuery, state: FSMContext):
    """
    Обрабатывает выбор даты из календаря.
    """
    selected_date = callback_query.data.split('_')[1]

    await state.update_data(selected_date=selected_date)
    await callback_query.message.answer(f"Вы выбрали дату: {selected_date}\nВведите название события:")
    await callback_query.answer()

    await state.set_state(WaitEvent.waiting_event_name)


@calendar_router.message(WaitEvent.waiting_event_name)
async def process_event_name(message: Message, state: FSMContext):
    """
    Обрабатывает название события.
    """
    event_name = message.text
    await state.update_data(event_name=event_name)
    await message.answer("Введите описание события:")
    await state.set_state(WaitEvent.waiting_event_description)


@calendar_router.message(WaitEvent.waiting_event_description)
async def process_event_description(message: Message, state: FSMContext):
    """
    Обрабатывает описание события.
    """
    event_description = message.text
    await state.update_data(event_description=event_description)
    await message.answer("Введите время события (в формате ЧЧ:ММ):")
    await state.set_state(WaitEvent.waiting_event_time)


@calendar_router.message(WaitEvent.waiting_event_time)
async def process_event_time(message: Message, state: FSMContext):
    """
    Обрабатывает время события и сохраняет данные в базу.
    """
    event_time = message.text
    try:
        # Проверяем формат времени
        datetime.strptime(event_time, "%H:%M")
        await state.update_data(event_time=event_time)

        # Сохраняем данные в базу
        user_data = await state.get_data()
        db.save_event(
            user_id=message.from_user.id,
            date=user_data['selected_date'],
            name=user_data['event_name'],
            description=user_data['event_description'],
            time=event_time
        )

        await message.answer(f"Событие сохранено:\n"
                             f"Дата: {user_data['selected_date']}\n"
                             f"Название: {user_data['event_name']}\n"
                             f"Описание: {user_data['event_description']}\n"
                             f"Время: {event_time}", reply_markup=comfirm_notif.notif_kb)
        await state.clear()
    except ValueError:
        await message.answer("Некорректный формат времени. Попробуйте ещё раз (в формате ЧЧ:ММ).")


@calendar_router.callback_query(F.data.startswith("prev_") | F.data.startswith("next_"))
async def process_navigation(callback_query: CallbackQuery):
    """
    Обрабатывает навигацию по календарю.
    """
    action, year, month = callback_query.data.split('_')
    year = int(year)
    month = int(month)
    await callback_query.message.edit_reply_markup(reply_markup=create_calendar(year, month))
    await callback_query.answer()  # Закрывает всплывающее уведомление


@calendar_router.callback_query(F.data == "ignore")
async def process_ignore(callback_query: CallbackQuery):
    """
    Игнорирует клики по заголовкам календаря.
    """
    await callback_query.answer()
