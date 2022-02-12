

"""
2This is a echo bot.
3It echoes any incoming text messages.
"""

import logging
from utils.set_bot_commands import set_default_commands
from loader import dp, storage
import handlers
from aiogram import executor

# Configure logging
logging.basicConfig(level=logging.INFO)

# On-startup function
async def on_startup(dispatcher):
    await set_default_commands(dispatcher)

# On-shutdown function
async def on_shutdown(dispatcher):
    await storage.close()
    logging.info('Bye!')

# run bot
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)
 