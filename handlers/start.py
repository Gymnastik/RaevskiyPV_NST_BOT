# Обработчик команды старт
from aiogram import types
from loader import dp, bot
from states.base import BotStates


@dp.message_handler(commands=['start'], state="*")
async def start_msg(msg, state):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button_start = types.KeyboardButton(text="/start")
    button_help = types.KeyboardButton(text="/help")
    button_nst = types.KeyboardButton(text="/user_style")
    button_gan1 = types.KeyboardButton(text="/Ukiyoe")
    button_gan2 = types.KeyboardButton(text="/VanGogh")
    keyboard.add(button_start, button_help)
    keyboard.row(button_nst)
    # keyboard.row(button_nst, button_gan1, button_gan2)
    await BotStates.content.set()
    await state.update_data(transfer_method=0)
    await bot.send_message(msg.chat.id, f'Привет, {msg.from_user.first_name}! Это бот для переноса стиля\
 с одного изображения (style), на другое (content). Для более подробной информации нажмите /help.',
                           reply_markup=keyboard)