import glob
import logging
import text_messages as ms

import keyboards as kb
from aiogram import types
from aiogram.dispatcher import FSMContext
from loader import bot, dp
from states.base import BotStates
from models import gatys

# Пишем в переменную описание загруженных стилей
with open("images/styles/styles_description.txt", encoding='UTF-8') as f:
    styles_text = f.read()
# Пишем в переменую изображения загруженных стилей
style_images = sorted([file for file in glob.glob('images/styles/*.jpg')])

# Хэндлеры описывающие процесс общения пользователя с ботом при вызове переноса стиля

# Хэндлер обрабатывающий нажатие кнопки "Главное меню" на inline-клавиатуре
@dp.callback_query_handler(text="menu", state='*')
async def transfer_style(call: types.CallbackQuery, state: FSMContext):
    
    await state.reset_state()
    await call.message.answer(ms.menu_message, parse_mode='Markdown', reply_markup=kb.start_keyboard())
    await call.answer()

# Хэндлер, обрабатывающий нажатие кнопки "Перенести стиль" на inline-клавиатуре
@dp.callback_query_handler(text="button_style", state='*')
async def transfer_style(call: types.CallbackQuery, state: FSMContext):
    
    await BotStates.style.set() 
    await call.message.answer("Мне нужно 2 фотографии. Сначала отправь фотографию стиля.\n"
                              "Если хочешь выбрать из доступных вариантов - нажми на кнопку ниже \U0001F447",
                              reply_markup=kb.style_images())
    await call.answer()

# Хэндлер, обрабатывающий нажатие кнопки "Выбрать картинку для стиля" на inline-клавиатуре 
@dp.callback_query_handler(text="style_images", state=BotStates.style)
async def transfer_style(call: types.CallbackQuery, state: FSMContext):
    
    await types.ChatActions.upload_photo()
    media = types.MediaGroup()
    for i, image in enumerate(style_images):
        if i == 0:
            media.attach_photo(types.InputFile(image), f"Есть следующие стили:\n\n{styles_text}")
        else:
            media.attach_photo(types.InputFile(image))
    
    await call.message.answer_media_group(media)
    await call.message.answer("Выбери стиль кнопкой, если ни один не нравится - отправляй собственную"
                              " картинку для стиля\n"
                              "Если ты используешь декстопную версию Telegram, то не забудь поставить галочку\n"
                             f"☑ `Compress images`", parse_mode='Markdown', reply_markup=kb.select_style())
    await call.answer()

# Хэндлер, обрабатывающий нажатие кнопок выбора стиля на inline-клавиатуре
@dp.callback_query_handler(lambda call: call.data.startswith('style_'), state=BotStates.style)
async def transfer_style(call: types.CallbackQuery, state: FSMContext):
    
    async with state.proxy() as data:
        data['style_img'] = style_images[int(call.data[-1])-1]
    await BotStates.content.set()
    await call.message.answer(f"Ты выбрал {int(call.data[-1])} стиль"
                              "\nТеперь отправь мне картинку, на которую нужно перенести стиль\n"
                              "Если ты используешь декстопную версию Telegram, то не забудь поставить галочку\n"
                             f"☑ `Compress images`", parse_mode='Markdown')
    await call.answer()

# Хэндлер, обрабатывающий нажатие кнопки "Примеры" на inline-клавиатуре
@dp.callback_query_handler(text="examples", state="*")
async def transfer_style(call: types.CallbackQuery):
    await types.ChatActions.upload_photo()
    media = types.MediaGroup()

    media.attach_photo(types.InputFile("./images/examples/Owl_example.jpg"), "Акварельная сова")
    media.attach_photo(types.InputFile("images/examples/Village_example.jpg"), "Деревня Пикассо")
    media.attach_photo(types.InputFile("images/examples/Wolf_example.jpg"), "Набросок волка")
    await call.message.answer_media_group(media)

    await call.message.answer('Надеюсь, тебе понравились эти примеры, и ты захотел попробовать\n\n'
                              'Жми на кнопку \U0001F447', reply_markup=kb.start_keyboard())
    await call.answer()

# Хэндлер, обрабатывающий картинку стиля от пользователя
@dp.message_handler(content_types = ['photo'], state='*')
async def style_download(msg: types.Message, state: FSMContext):
    current_state = await state.get_state()
    logging.info(current_state)
    logging.info(current_state == 'BotStates:style')
    image = msg.photo[-1]
    img = await bot.download_file_by_id(image.file_id)
    
    if current_state == 'BotStates:style':
        async with state.proxy() as data:
            data['style_img'] = img
        await BotStates.content.set()
        await msg.answer("Теперь отправь мне картинку, на которую нужно перенести стиль")
        
    elif current_state == 'BotStates:content':
        async with state.proxy() as data:
            data['content_img'] = img
        data = await state.get_data()
        style_img = data['style_img']
        content_img = data['content_img']
        await state.reset_state()
        await msg.answer("Идёт обработка, это может занять около 5 минут...  \n\U000023F1   \U000023F1   \U0001F51C")
        result = gatys.run_nst(style_img, content_img)
        await bot.send_photo(msg.chat.id, result)
        await msg.answer("Готово! \U0001F44D\U0001F44D \n\nЕсли хочешь попробовать еще, жми \U0001F447\U0001F447", reply_markup=kb.start_keyboard())
    
    else:
        await msg.answer("Прежде чем отправлять мне картинки нажми кнопку\n *Перенести стиль* \U0001F447", 
                         parse_mode='Markdown', reply_markup=kb.start_keyboard())

