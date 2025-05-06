from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

markup = InlineKeyboardMarkup()
for event in events:
    button_text = f"{event['date']} {event['time']} - {event['name']}"
    callback_data = f"delete_{event['date']}_{event['time']}"
    markup.add(InlineKeyboardButton(text=button_text, callback_data=callback_data))
