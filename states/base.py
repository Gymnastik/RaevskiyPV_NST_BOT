from aiogram.dispatcher.filters.state import State, StatesGroup


class BotStates(StatesGroup):
    """
      Класс - машина состояний для бота. Content - состояние обработки фото контента,
      style - состояние обработки фото стиля
    """
    content = State()
    style = State()