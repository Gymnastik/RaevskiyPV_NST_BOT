from aiogram import Dispatcher, Bot
from dotenv import load_dotenv
from os import environ
from aiogram.contrib.fsm_storage.memory import MemoryStorage


load_dotenv()
BOT_TOKEN = environ.get('BOT_TOKEN')

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)