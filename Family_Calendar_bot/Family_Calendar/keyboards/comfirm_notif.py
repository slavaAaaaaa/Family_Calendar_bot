from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

notif_kb = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Создать уведомление", callback_data="create_notif")],
                     [InlineKeyboardButton(text="Не создавать уведомление", callback_data='cancel_notif')],
                     ]
)
