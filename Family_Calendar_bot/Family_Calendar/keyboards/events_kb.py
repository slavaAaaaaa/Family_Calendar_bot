from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

choice_kb = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Добавить событие", callback_data="add_event")],
                     [InlineKeyboardButton(text="Удалить событие", callback_data='delete_event')],
                     [InlineKeyboardButton(text='Пока хз', callback_data='3')]
                     ]
)