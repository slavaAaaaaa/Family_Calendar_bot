from aiogram import Router, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

from database import Database
import database
import asyncio
start_router = Router()
db = Database()

@start_router.message(CommandStart())
async def start_message(message: Message):
    await message.answer(f"Привет!(⁠•⁠‿⁠•⁠)\nЯ ваш 'Семейный календарь'! ♡⁠♡⁠♡\n"
                         f"✧⁠◝⁠(⁠⁰⁠▿⁠⁰⁠)⁠◜⁠✧\nЯ помогу вам составить календарь всех главных и важных событий, проведенных в кругу важных и дорогих для вас людей!\n(⁠灬⁠º⁠‿⁠º⁠灬⁠)⁠♡\n/help - выводит все команды для использования чат-бота; ")
    await asyncio.sleep(0.5)
    await message.answer_sticker("CAACAgIAAxkBAAEO6BxoGhRgXmif7iP_xDeDMXY0BuWLZgAChwIAAladvQpC7XQrQFfQkDYE")
    username = message.from_user.username
    user_id = message.from_user.id
    db.add_user(user_id, username)