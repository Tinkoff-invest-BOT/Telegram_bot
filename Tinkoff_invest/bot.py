import logging
from aiogram import Bot, Dispatcher, executor, types
import markups as nav
from functions import tocken_check
from db import Database

TOKEN = '6308347573:AAHRkAHGuBCmw_cDgm8J9z1pA3N9AZZ3bb8'
logging.basicConfig(level=logging.INFO)
bot = Bot(TOKEN)
dp = Dispatcher(bot)

db = Database('database')


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if (not db.user_exists(message.from_user.id)):
        db.add_user(message.from_user.id)
        await bot.send_message(message.from_user.id, f'Привет, {message.chat.first_name}! \n Укажи свой ник:')
    else:
        await bot.send_message(message.from_user.id, "Вы уже зарегистрированны!", reply_markup=nav.mainMenu)


@dp.message_handler()
async def bot_message(message: types.Message):
    if message.chat.type == 'private':
        if message.text == "ПРОФИЛЬ" or message.text == "ПОДПИСКА":
            pass
        else:
            if db.get_signup(message.from_user.id) == 'setnickname':
                if (len(message.text) > 15):
                    await bot.send_message(message.from_user.id, 'Никнейм не должен превышать 15 символов')
                elif '@' in message.text or '/' in message.text:
                    await bot.send_message(message.from_user.id, 'Вы ввели запрещенный символ')
                else:
                    db.set_nickname(message.from_user.id, message.text)
                    db.set_sign_up(message.from_user.id, "setemail")
                    await bot.send_message(message.from_user.id, 'Введите  свой email', reply_markup=nav.mainMenu)
            elif db.get_signup(message.from_user.id) == 'setemail':
                if (len(message.text) < 5):
                    await bot.send_message(message.from_user.id, "Недопустимый email")
                elif '@' not in message.text or '.' not in message.text:
                    await bot.send_message(message.from_user.id, 'Недопустимый формат email')
                else:
                    db.set_email(message.from_user.id, message.text)
                    db.set_sign_up(message.from_user.id, 'settoken')
                    await bot.send_message(message.from_user.id, 'Введите токен от своего аккаунта Тинькофф Инвестиции')
            elif db.get_signup(message.from_user.id) == 'settoken':
                if tocken_check(message.text) == 1:
                    await bot.send_message(message.from_user.id, 'Несуществующий токен')
                elif tocken_check(message.text) == 2:
                    await bot.send_message(message.from_user.id,
                                           'Ты когда нибудь видел токен на русском языке? Напиши нормальный токен')
                elif tocken_check(message.text) == 3:
                    await bot.send_message(message.from_user.id, 'Я такое не понимаю...')

                else:
                    db.set_tocken(message.from_user.id, message.text)
                    db.set_sign_up(message.from_user.id, 'done')
                    await bot.send_message(message.from_user.id, 'Ваш аккаунт зарегестрирован!')


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
