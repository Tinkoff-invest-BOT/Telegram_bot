import logging
import matplotlib.pyplot as plt
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from tabulate import tabulate
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from parser_daily import notify_user_about_stocks
from datetime import datetime, timedelta

from io import BytesIO
from functions import *
from db import Database
from passwords import *
from connection_db import connection
from messages import *
import asyncio


storage = MemoryStorage()
logging.basicConfig(level=logging.INFO)
bot_run = Bot(BOT_TOKEN)
dp = Dispatcher(bot_run, storage=storage)
db = Database(connection)


def ff():
    from temporary import df

class Form(StatesGroup): 
    '''
    Этот класс нужен для того, чтобы запоминать состояние разговора с пользователем ()
    '''
    waiting_for_tickers = State()
    confirmation = State() 

@dp.message_handler(lambda message: db.user_exists(message.from_user.id) == False)
async def why_without_start(message):
    db.add_user(message.from_user.id)
    await bot_run.send_message(message.from_user.id, start_message)
    await bot_run.send_message(message.from_user.id, f'{message.chat.first_name}, выбери себе ник:')
    db.set_sign_up(message.from_user.id, 'setnickname')



@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if(not db.user_exists(message.from_user.id)):
        db.add_user(message.from_user.id)
        await bot_run.send_message(message.from_user.id, start_message)
        await bot_run.send_message(message.from_user.id, f'{message.chat.first_name}, выбери себе ник:')
        db.set_sign_up(message.from_user.id, 'setnickname')
    elif db.get_signup(message.from_user.id) == 'done' or db.get_signup(message.from_user.id) == 'withouttoken':
        await bot_run.send_message(message.from_user.id, "Вы уже зарегистрированны!")
    else:
        await bot_run.send_message(message.from_user.id, "Продолжайте регистрацию")



@dp.message_handler(commands=['help'])
async def help(message: types.Message):
    await bot_run.send_message(message.from_user.id, help_message)
    if(not db.user_exists(message.from_user.id)):
        await start(message)

    elif db.get_signup(message.from_user.id) == 'done':
        pass
    elif db.get_signup(message.from_user.id) == 'withouttoken':
        pass
    else:
        await bot_run.send_message(message.from_user.id, 'Продолжайте регистрацию!')



@dp.message_handler(lambda message: db.get_signup(message.from_user.id) == "setnickname")
async def nick_setter(message: types.Message):
    if (len(message.text) > 30):
        await bot_run.send_message(message.from_user.id, 'Никнейм не должен превышать 30 символов')
    elif '@' in message.text or '/' in message.text:
        await bot_run.send_message(message.from_user.id, 'Вы ввели запрещенный символ')
    else:
        db.set_nickname(message.from_user.id, message.text)
        db.set_sign_up(message.from_user.id, "setemail")
        await bot_run.send_message(message.from_user.id, 'Введите  свой email')



@dp.message_handler(lambda message: db.get_signup(message.from_user.id) == 'setemail')
async def mail_setter(message: types.Message):
    if (len(message.text) < 5):
        await bot_run.send_message(message.from_user.id, "Недопустимый email")
    elif '@' not in message.text or '.' not in message.text:
        await bot_run.send_message(message.from_user.id, 'Недопустимый формат email')
    else:
        db.set_email(message.from_user.id, message.text)
        db.set_sign_up(message.from_user.id, 'settoken')
        await bot_run.send_message(message.from_user.id, 'Введите токен от своего аккаунта Тинькофф Инвестиции\nВы можете продолжить без токена, но тогда будет доступно гораздо меньше возможностей.\nДля этого напиши "/without_token"')



@dp.message_handler(lambda message: db.get_signup(message.from_user.id) == 'settoken')
async def tkn_setter(message: types.Message):
    if message.text == '/without_token':
        await bot_run.send_message(message.from_user.id, 'Вам доступен функционал, для которого не требуется токен.\nЕсли захотите вести токен, это всегда можно сделать, вызвав команду "/settoken"')
        db.set_sign_up(message.from_user.id, 'withouttoken')
        db.set_status(message.from_user.id, "none")
    else:
        if token_check(message.text) == 1:
            await bot_run.send_message(message.from_user.id, 'Несуществующий токен')
        elif token_check(message.text) == 2:
            await bot_run.send_message(message.from_user.id,
                                   'Ты когда нибудь видел токен на русском языке? Напиши нормальный токен')
        elif token_check(message.text) == 3:
            await bot_run.send_message(message.from_user.id, 'Я такое не понимаю...')

        else:
            db.set_tocken(message.from_user.id, message.text)
            db.set_sign_up(message.from_user.id, 'done')
            await bot_run.send_message(message.from_user.id, 'Ваш аккаунт зарегестрирован!')



@dp.message_handler(lambda message: message.text == "/settoken")
async def status_set_token(message: types.Message):
    db.set_status(message.from_user.id, "token_setter")
    await bot_run.send_message(message.from_user.id, 'Введите токен от своего аккаунта Тинькофф Инвестиции\nВы можете продолжить без токена, но тогда будет доступно гораздо меньше возможностей.\nДля этого напиши "/without_token"')
    
    
    
@dp.message_handler(lambda message: db.get_status(message.from_user.id) == "token_setter")
async def token_setter(message: types.Message):
    if message.text == '/without_token':
        await bot_run.send_message(message.from_user.id, 'Вам доступен функционал, для которого не требуется токен.\nЕсли захотите вести токен, это всегда можно сделать, вызвав команду "/settoken"')
        db.set_sign_up(message.from_user.id, 'withouttoken')
        db.set_status(message.from_user.id, "none")
    else:
        if token_check(message.text) == 1:
            await bot_run.send_message(message.from_user.id, 'Несуществующий токен')
        elif token_check(message.text) == 2:
            await bot_run.send_message(message.from_user.id,
                                   'Ты когда нибудь видел токен на русском языке? Напиши нормальный токен')
        elif token_check(message.text) == 3:
            await bot_run.send_message(message.from_user.id, 'Я такое не понимаю...')
        else:
            db.set_tocken(message.from_user.id, message.text)
            db.set_sign_up(message.from_user.id, 'done')
            db.set_status(message.from_user.id, "none")
            await bot_run.send_message(message.from_user.id, 'Ваш аккаунт обновлен!')



@dp.message_handler(lambda message: message.text == "/without_token")
async def continue_without_token(message:types.Message):
    if (not db.user_exists(message.from_user.id)):
        db.add_user(message.from_user.id)
        await bot_run.send_message(message.from_user.id, f'Приветствую, {message.chat.first_name}! \n Укажите свой ник:')
    else:
        if db.get_signup(message.from_user.id) == 'done':
            await bot_run.send_message(message.from_user.id, 'Вы уже ввели токен, Вам доступны все функции!')
        elif db.get_signup(message.from_user.id) != 'settoken':
            await bot_message(message)
        elif db.get_signup(message.from_user.id) == 'withouttoken':
            await bot_run.send_message(message.from_user.id, 'Вам уже доступен функционал, для которого не требуется токен.\nЕсли захотите вести или изменить токен, это всегда можно сделать, вызвав команду "/settoken"')
        else:
            await bot_run.send_message(message.from_user.id, 'Вам доступен функционал, для которого не требуется токен.\nЕсли захотите ввести или изменить токен, введите команду "/settoken"')
            db.set_sign_up(message.from_user.id, 'withouttoken')



@dp.message_handler(lambda message: message.text == "/get_portfolio")
async def get_portfolio(message: types.Message):
    if db.get_signup(message.from_user.id) != 'done':
        await bot_run.send_message(message.from_user.id, 'Извините, но эта функция не работает без токена. Чтобы установить свой токен введите команду /settoken.\nУзнать доступные функции можно с помощью команды /help')
    else:
        ff()
        pdf_out = create_pdf_from_dataframe(df)
        pdf_out.seek(0)
        await bot_run.send_document(message.from_user.id, document=types.InputFile(pdf_out, filename='your_portfolio.pdf'))
        
    plt.bar(df['figi'], df['quantity'])
    plt.xlabel('Share')
    plt.ylabel('Quantity')
    plt.title('Я самый крутой мазафака')
    plt.savefig('tmp.png')
    await bot_run.send_photo(message.from_user.id, photo=open('tmp.png', 'rb'))



@dp.message_handler(lambda message: message.text == '/set_shares')
async def shares_setter(message: types.Message):
    if db.get_share(message.from_user.id) == []:
        await Form.waiting_for_tickers.set()
        await bot_run.send_message(message.from_user.id, 'Пожалуйста, введите через запятую *до 10 тикеров* (коротких названий) ценных бумаг, вы хотите отслеживать у которых Вы желаете отслеживать стоимость:')
    else:
        await Form.confirmation.set()
        await bot_run.send_message(message.from_user.id, 'У вас уже есть набор ценных бумаг. Желаете изменить его?')


@dp.message_handler(state=Form.waiting_for_tickers)
async def process_tickers(message: types.Message, state):
    tickers = message.text
    db.set_share(user_id=message.from_user.id, shares_list=tickers.split(', '))
    await bot_run.send_message(message.from_user.id, 'Вы удачно изменили набор ценных бумаг!')
    
    await state.finish()


@dp.message_handler(state=Form.confirmation)
async def process_confirmation(message: types.Message, state):
    if message.text.lower() == 'да':
        await Form.waiting_for_tickers.set()
        await bot_run.send_message(message.from_user.id, 'Пожалуйста, введите новый список тикеров через запятую:')
    elif message.text.lower() == 'нет':
        await bot_run.send_message(message.from_user.id, 'Хорошо. Вы можете сделать это в любой момент, если введёте команду "/set_shares"')
        await state.finish()



@dp.message_handler()
async def bot_message(message: types.Message):
    if message.chat.type == 'private':
        if (not db.user_exists(message.from_user.id)):
            db.add_user(message.from_user.id)
            await bot_run.send_message(message.from_user.id, start_message)
            await bot_run.send_message(message.from_user.id, f'{message.chat.first_name}, выберите себе ник:')
            db.set_sign_up(message.from_user.id, 'setnickname')
        else:
            await bot_run.send_message(message.from_user.id, 'Очень интересно, но ничего не понятно\nЧтобы узнать доступные команды, введите /help')
    else:
        await bot_run.send_message(message.from_user.id, 'Я работаю только в личных чатаx')


async def eleven_messages():
    '''
    Эта функция рассылает пользователям информацию о стоимости выбранных ими акций каждый день в 11:00
    '''
    users = db.get_all_users()
    for user_id in users:
        await bot_run.send_message(user_id, notify_user_about_stocks(user_id=user_id))
        


if __name__ == "__main__":
    
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(eleven_messages, trigger="cron", hour=11, minute=1)
    
    scheduler.start()
    executor.start_polling(dp, skip_updates=True)
