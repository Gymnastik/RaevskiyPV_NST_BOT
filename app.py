import logging
from utils.set_bot_commands import set_default_commands # грузим функцию настройки дефолтных команд бота
from loader import dp, storage
import handlers # Импортируем хэндлеры, в инитах пакетов прописана последовательность инициализации
from aiogram import executor

# Конфигурируем логирование
logging.basicConfig(level=logging.INFO)

# Функция, которая запускается при старте бота
async def on_startup(dispatcher):
    await set_default_commands(dispatcher)

# Функция, которая запускается при отключении бота
async def on_shutdown():
    await storage.close()
    logging.info('Bye!')

# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)
    