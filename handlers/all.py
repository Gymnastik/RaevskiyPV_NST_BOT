
from aiogram import types
from loader import dp
import keyboards as kb
import text_messages as ms


# Эхо хендлер, куда летят текстовые сообщения без указанного состояния
@dp.message_handler(state='*')
async def bot_echo(message: types.Message):
    await message.answer('Я бы пообщался с тобой,'
                         '\nно мне пока не написали такой функционал'
                         f'\n{ms.menu_message} \U0001F447', reply_markup=kb.start_keyboard())
