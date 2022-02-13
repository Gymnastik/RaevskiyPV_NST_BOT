# Обработчик команды старт
from aiogram import types
from loader import dp
from aiogram.dispatcher import FSMContext
import text_messages as ms
import keyboards as kb


@dp.message_handler(commands=['start'], state="*")
async def start_msg(msg: types.Message, state: FSMContext):
    
    await msg.answer(f"Привет, {msg.from_user.first_name}{ms.start_message}", parse_mode='Markdown', reply_markup=kb.start_keyboard())