from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
import asyncio


help_router = Router()

@help_router.message(Command("help"))
async def help(message: Message):
    await message.answer(f"/start — приветствие и краткое описание команд;\n/help — выводит все команды для использования чат-бота;\n /calendar — добавляет событие на указанную дату;\n/delete_events — удаляет событие, выбранное пользователем;\n"
                         f"/show_events — выводит все добавленные события;\n/send — отправляет сообщение члену семьи;")
    await asyncio.sleep(0.5)
    await message.answer_sticker("CAACAgIAAxkBAAEO6DBoGhXGkWXCjTC_QqVQwZLnmqadjgACcwIAAladvQqoc6WsC0Ee0TYE")