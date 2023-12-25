from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
#
# btnProfile = KeyboardButton("ПРОФИЛЬ")
# btnSub = KeyboardButton("ПОДПИСКА")
# btnHelp = KeyboardButton('/help')
# btnSettoken = KeyboardButton('/settoken')
#
# mainMenu = ReplyKeyboardMarkup(resize_keyboard=True)
# mainMenu.add(btnProfile, btnSub)

main_menu = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
main_menu.add(KeyboardButton('Профиль'), KeyboardButton('Функции'))

without_token = ReplyKeyboardMarkup(resize_keyboard=True)
without_token.add(KeyboardButton('Without token'))

yes_no = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
yes_no.add(KeyboardButton('Да'), KeyboardButton('Нет'))

to_main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
to_main_menu.add(KeyboardButton('В главное меню'))

operations = ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
operations.add(KeyboardButton('1'), KeyboardButton('2'), KeyboardButton('3'), KeyboardButton('4'))
operations.add(KeyboardButton('В главное меню'))

analyzer_tickers = ReplyKeyboardMarkup(resize_keyboard=True)
analyzer_tickers.add(KeyboardButton('Использовать shares'))
analyzer_tickers.add(KeyboardButton('В главное меню'))

