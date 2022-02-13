from aiogram import Dispatcher, Bot
from dotenv import load_dotenv
from os import environ
import asyncio
from aiogram.contrib.fsm_storage.memory import MemoryStorage


load_dotenv()
BOT_TOKEN = environ.get('BOT_TOKEN')


# Создаём бота, loop, хранилище и диспетчер
loop = asyncio.get_event_loop()
bot = Bot(token=BOT_TOKEN, loop=loop)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)