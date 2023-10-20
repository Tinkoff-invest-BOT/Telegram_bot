from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

btnProfile = KeyboardButton("ПРОФИЛЬ")
btnSub = KeyboardButton("ПОДПИСКА")

mainMenu = ReplyKeyboardMarkup(resize_keyboard=True)
mainMenu.add(btnProfile, btnSub)