from aiogram import types
from loader import dp, bot
import logging
import keyboards as kb

@dp.message_handler(commands=['help'], state="*")
async def help_msg(msg):
    logging.info(f"New User!", msg.chat.id)
    await msg.answer(kb.start_message, reply_markup=kb.start_keyboard())
    await bot.send_message(msg.chat.id, "Команды чат-бота:\n/start - начало работы и общий сброс\n/help\
 - помощь\n/user_style - стиль пользователя (это режим по умолчанию). Сначала надо загрузить изображение content,\
 затем изображение style\n/Ukiyoe - к изображению, загруженному пользователем, будет применен японский стиль Укиё-э\
\n/VanGogh - к изображению, загруженному пользователем, будет применен стиль художника Ван Гога.\n\n Методы стилизации Ukiyoe\
 и VanGogh (основаны на сетях GAN) применяются быстро, метод user_style может занять некоторое время (до минуты).")