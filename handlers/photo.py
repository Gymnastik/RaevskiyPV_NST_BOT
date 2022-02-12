from aiogram import types
from loader import dp, bot
import keyboards as kb
from PIL import Image, ImageOps
import logging
import io

@dp.message_handler(content_types = ['photo'], state="*")
async def help_msg(msg):
    image = msg.photo[-1]
    file_info = await bot.get_file(image.file_id)
    img = await bot.download_file(file_info.file_path)
    ttt = Image.open(img)
    ttt = ImageOps.contain(ttt,(256,256))
    bio = io.BytesIO()
    bio.name ='output.jpeg'
    ttt.save(bio, 'JPEG')
    bio.seek(0)
    logging.info(type(ttt))
    await bot.send_photo(msg.chat.id,bio)
    await msg.answer('Я переслал тебе твоё же фото')
