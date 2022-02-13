from aiogram import types

def start_keyboard():
    buttons = [
        types.InlineKeyboardButton(text="\U00002194 Перенести стиль", callback_data="button_style"),
        types.InlineKeyboardButton(text="\U0001F307 Примеры", callback_data="examples"),
        types.InlineKeyboardButton(text="\U0001F47E GitHub", url='https://github.com/Gymnastik/RaevskiyPV_NST_BOT')
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)

    return keyboard

def style_images():
    buttons = [
        types.InlineKeyboardButton(text="Выбрать картинку для стиля", callback_data="style_images"),
        types.InlineKeyboardButton(text="Главное меню", callback_data="menu")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)

    return keyboard


def select_style():
    buttons = [
        types.InlineKeyboardButton(text="1️⃣", callback_data="style_1"),
        types.InlineKeyboardButton(text="2️⃣", callback_data="style_2"),
        types.InlineKeyboardButton(text="3️⃣", callback_data="style_3"),
        types.InlineKeyboardButton(text="4️⃣", callback_data="style_4"),
        types.InlineKeyboardButton(text="5️⃣", callback_data="style_5"),
        types.InlineKeyboardButton(text="6️⃣", callback_data="style_6"),
        types.InlineKeyboardButton(text="Главное меню", callback_data="menu")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2).add(*buttons)

    return keyboard