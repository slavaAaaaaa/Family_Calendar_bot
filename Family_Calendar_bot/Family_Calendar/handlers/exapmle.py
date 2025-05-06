from aiogram import Router, F
from aiogram.types import Message

example_router = Router()

@example_router.message(F.text == "Обычные кнопки")
async def show_simple_kb(message: Message):
    await message.answer("Вот", reply_markup=start_kb.simple_kb)

@example_router.message(F.text == "Инлайн кнопки")
async def show_inline_kb(message: Message):
    await message.answer("Вот", reply_markup=start_kb.inline_kb)
