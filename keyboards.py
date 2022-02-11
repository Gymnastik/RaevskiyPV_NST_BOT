from aiogram import types

def start_keyboard():
    buttons = [
        types.InlineKeyboardButton(text="Перенести стиль", callback_data="button_style"),
        types.InlineKeyboardButton(text="Лето в зиму", callback_data="summer2winter"),
        types.InlineKeyboardButton(text="Зиму в лето", callback_data="winter2summer"),
        types.InlineKeyboardButton(text="\U0001F4A5 Примеры", callback_data="examples"),
        types.InlineKeyboardButton(text="\U0001F4C3 GitHub", url='https://github.com/mayo889/Telegram_Bot_NST_GAN')
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)

    return keyboard

start_message = ("Привет! \U0001F44B\n\n"
                 "Я умею создавать новые фотографии с помощью нейронных сетей.\n\n"
                 "\U00002705 Ты можешь отправить мне 2 фотографии: с первой фотографии я заберу стиль и "
                 "перенесу его на твою вторую фотографию.\n\n"
                 "\U00002705 Если у тебя есть какая-нибудь летняя фотография, то я могу сделать так, будто она "
                 "была сделана зимой\n\n"
                 "\U00002705 Или наоборот, если есть зимняя фотография, то с легкостью превращу ее в летнюю\n\n"
                 "Я подготовил для тебя примеры, нажимай на кнопку и взгляни\n\n"
                 "Если станет интересно, как это все работает, "
                 "то можешь ознакомиться со страницей проекта на GitHub")

menu_message = ("Напомню, что я умею делать:\n\n"
                "\U00002705 Переносить стиль одной фотографии на другую\n\n"
                "\U00002705 Превратить летнюю фотографию в зимнию\n\n"
                "\U00002705 Превратить зимнюю фотографию в летнюю\n\n"
                "Если я неправильно работаю, то попробуй перезапустить меня командой /start")