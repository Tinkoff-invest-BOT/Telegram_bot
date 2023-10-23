import logging
from aiogram import Bot, Dispatcher, executor, types
import markups as nav
from functions import *
from db import Database
from passwords import *
from connection_db import connect
from messages import *


logging.basicConfig(level=logging.INFO)
bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot)

db = Database(connect)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if(not db.user_exists(message.from_user.id)):
        db.add_user(message.from_user.id)
        await bot.send_message(message.from_user.id, start_message)
        await bot.send_message(message.from_user.id, f'{message.chat.first_name}, выбери себе ник:')
    elif  db.get_signup(message.from_user.id) == 'done' or db.get_signup(message.from_user.id) == 'withouttoken':
        await bot.send_message(message.from_user.id, "Вы уже зарегистрированны!", reply_markup=nav.mainMenu)
    else:
        await bot.send_message(message.from_user.id, "Продолжайте регистрацию")


@dp.message_handler(commands=['help'])
async def help(message: types.Message):
    await bot.send_message(message.from_user.id, help_message)
    if(not db.user_exists(message.from_user.id)):
        await start(message)

    elif db.get_signup(message.from_user.id) == 'done':
        pass
    elif db.get_signup(message.from_user.id) == 'withouttoken':
        pass
    else:
        await bot.send_message(message.from_user.id,'Продолжайте регистрацию!')



@dp.message_handler(lambda message: message.text == "/settoken")
async def status_set_token(message: types.Message):
    db.set_status(message.from_user.id, "token_setter")
    await bot.send_message(message.from_user.id,'Введите токен от своего аккаунта Тинькофф Инвестиции\nВы можете продолжить без токена, но тогда будет доступно гораздо меньше возможностей.\nДля этого напиши "/without_token"')
@dp.message_handler(lambda message: db.get_status(message.from_user.id) == "token_setter")
async def token_setter(message: types.Message):
    if message.text == '/without_token':
        await bot.send_message(message.from_user.id,'Вам доступен функционал, для которого не требуется токен.\nЕсли захотите вести токен, это всегда можно сделать, вызвав команду "/settoken"')
        db.set_sign_up(message.from_user.id, 'withouttoken')
        db.set_status(message.from_user.id, "none")

    else:
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
            db.set_status(message.from_user.id, "none")
            await bot.send_message(message.from_user.id, 'Ваш аккаунт обновлен!')






@dp.message_handler(lambda message: message.text == "/without_token")
async def continue_without_token(message:types.Message):
    if (not db.user_exists(message.from_user.id)):
        db.add_user(message.from_user.id)
        await bot.send_message(message.from_user.id, f'Привет, {message.chat.first_name}! \n Укажи свой ник:')
    else:
        if db.get_signup(message.from_user.id) == 'done':
            await bot.send_message(message.from_user.id, 'Но вы уже ввели токен, Вам доступны все функции!')
        elif db.get_signup(message.from_user.id) != 'settoken':
            await bot_message(message)
        elif db.get_signup(message.from_user.id) == 'withouttoken':
            await bot.send_message(message.from_user.id, 'Вам уже доступен функционал, для которого не требуется токен.\nЕсли захотите вести или изменить токен, это всегда можно сделать, вызвав команду "/settoken"')
        else:
            await bot.send_message(message.from_user.id, 'Вам доступен функционал, для которого не требуется токен.\nЕсли захотите вести или изменить токен, это всегда можно сделать, вызвав команду "/settoken"')
            db.set_sign_up(message.from_user.id, 'withouttoken')




@dp.message_handler()
async def bot_message(message: types.Message):
    if message.chat.type == 'private':
        if (not db.user_exists(message.from_user.id)):
            await start(message)
        else:
            if db.get_signup(message.from_user.id) == 'setnickname':
                if(len(message.text) > 30):
                    await bot.send_message(message.from_user.id, 'Никнейм не должен превышать 30 символов')
                elif '@' in message.text or '/' in message.text:
                    await bot.send_message(message.from_user.id, 'Вы ввели запрещенный символ')
                else:
                    db.set_nickname(message.from_user.id, message.text)
                    db.set_sign_up(message.from_user.id, "setemail")
                    await bot.send_message(message.from_user.id, 'Введите  свой email', reply_markup=nav.mainMenu)
            elif db.get_signup(message.from_user.id) == 'setemail':
                if(len(message.text) < 5):
                    await bot.send_message(message.from_user.id, "Недопустимый email")
                elif '@' not in message.text or '.' not in message.text:
                    await bot.send_message(message.from_user.id, 'Недопустимый формат email')
                else:
                    db.set_email(message.from_user.id, message.text)
                    db.set_sign_up(message.from_user.id, 'settoken')
                    await bot.send_message(message.from_user.id, 'Введите токен от своего аккаунта Тинькофф Инвестиции\nВы можете продолжить без токена, но тогда будет доступно гораздо меньше возможностей.\nДля этого напиши "/without_token"')
            elif db.get_signup(message.from_user.id) == 'settoken':
                if tocken_check(message.text) == 1:
                    await bot.send_message(message.from_user.id, 'Несуществующий токен')
                elif tocken_check(message.text) == 2:
                    await bot.send_message(message.from_user.id, 'Ты когда нибудь видел токен на русском языке? Напиши нормальный токен')
                elif tocken_check(message.text) == 3:
                    await bot.send_message(message.from_user.id, 'Я такое не понимаю...')

                else:
                    db.set_tocken(message.from_user.id, message.text)
                    db.set_sign_up(message.from_user.id, 'done')
                    await bot.send_message(message.from_user.id, 'Ваш аккаунт зарегестрирован!')
            else:
                await bot.send_message(message.from_user.id, 'Очень интересно, но ничего не понятно\nЧто бы узнать доступные команды, введи /help')

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates = True)



