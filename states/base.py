from aiogram.dispatcher.filters.state import State, StatesGroup


class BotStates(StatesGroup):
    """
      Класс - машина состояний для бота. 
      style - состояние обработки фото стиля,
      сontent - состояние обработки фото контента
    """
    style = State()
    content = State()
 