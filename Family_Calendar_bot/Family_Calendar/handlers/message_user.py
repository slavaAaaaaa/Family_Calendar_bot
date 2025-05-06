from aiogram import Router, Bot, types
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from database import Database

message_router = Router()

db = Database()


class MessageStates(StatesGroup):
    waiting_for_recipient = State()
    waiting_for_message = State()


@message_router.message(Command("send"))
async def start_sending(message: Message, state: FSMContext):
    await message.answer("Введите имя пользователя, которому хотите отправить сообщение:")
    await state.set_state(MessageStates.waiting_for_recipient)


@message_router.message(MessageStates.waiting_for_recipient)
async def set_recipient(message: Message, state: FSMContext):
    recipient_username = message.text.strip()


    if recipient_username.startswith('@'):
        recipient_username = recipient_username[1:]


    recipient = db.get_user_by_username(recipient_username)
    if not recipient:
        await message.answer("Пользователь с таким именем не найден. Попробуйте снова.")
        return


    recipient_id = recipient[1]
    await state.update_data(recipient_id=recipient_id)

    await message.answer("Введите сообщение, которое хотите отправить:")
    await state.set_state(MessageStates.waiting_for_message)


@message_router.message(MessageStates.waiting_for_message)
async def send_message_to_user(message: Message, state: FSMContext, bot: Bot):
    user_data = await state.get_data()
    recipient_id = user_data["recipient_id"]

    try:

        await bot.send_message(
            recipient_id,
            f"Вам сообщение от @{message.from_user.username}:\n\n{message.text}"
        )
        await message.answer("Сообщение успешно отправлено!")
    except Exception as e:
        await message.answer("Не удалось отправить сообщение. Возможно, пользователь ещё не начал диалог с ботом.")
        print(f"Ошибка отправки сообщения: {e}")
    finally:
        await state.clear()


