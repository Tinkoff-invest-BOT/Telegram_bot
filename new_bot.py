import types
from functions import *
from db import Database
from passwords import *
from connection_db import connection
from messages import *
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot, Dispatcher, executor, types
from parser_daily import notify_user_about_stocks, price_checker
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup


logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
bot_run = Bot(BOT_TOKEN)
dp = Dispatcher(bot_run, storage=storage)
db = Database(connection)

class Form(StatesGroup):
    '''
    Этот класс нужен для того, чтобы запоминать состояние разговора с пользователем
    '''
    waiting_for_tickers = State()
    confirmation = State()

@dp.message_handler(lambda message: db.user_exists(message.from_user.id) == False)
async def start_function(message):
    db.add_user(message.from_user.id)
    await bot_run.send_message(message.from_user.id, start_message)
    await bot_run.send_message(message.from_user.id, f'{message.chat.first_name}, выбери себе ник:')
    db.set_sign_up(message.from_user.id, 'setnickname')


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if not db.user_exists(message.from_user.id):
       await start_function(message)
    elif db.get_signup(message.from_user.id) == 'done':
        await bot_run.send_message(message.from_user.id, "Вы уже зарегистрированны!")
    else:
        await bot_run.send_message(message.from_user.id, 'Продолжайте регистрацию!')


@dp.message_handler(commands=['help'])
async def help_function(message: types.Message):
    await bot_run.send_message(message.from_user.id, help_message, parse_mode='html')
    if not db.user_exists(message.from_user.id):
        await start(message)
    elif db.get_signup(message.from_user.id) != 'done':
        await bot_run.send_message(message.from_user.id, 'Продолжайте регистрацию!')


@dp.message_handler(lambda message: db.get_signup(message.from_user.id) == 'setnickname')
async def nick_setter(message: types.Message):
    if len(message.text) > 30:
        await bot_run.send_message(message.from_user.id, 'Никнейм не должен превышать 30 символов')
    elif '@' in message.text or '/' in message.text:
        await bot_run.send_message(message.from_user.id, 'Вы ввели запрещенный символ')
    else:
        db.set_nickname(message.from_user.id, message.text)
        db.set_sign_up(message.from_user.id, 'setemail')
        await bot_run.send_message(message.from_user.id, 'Введите  свой email')


@dp.message_handler(lambda message: db.get_signup(message.from_user.id) == 'setemail')
async def mail_setter(message: types.Message):
    if len(message.text) < 5:
        await bot_run.send_message(message.from_user.id, "Недопустимый email")
    elif '@' not in message.text or '.' not in message.text:
        await bot_run.send_message(message.from_user.id, 'Недопустимый формат email')
    else:
        db.set_email(message.from_user.id, message.text)
        db.set_sign_up(message.from_user.id, 'settoken')
        await bot_run.send_message(message.from_user.id, 'Введите токен от своего аккаунта Тинькофф <a href="https://developer.tinkoff.ru/docs/intro/manuals/self-service-auth">Как получить токен Tinkoff </a>\
                                                         Инвестиции\nВы можете продолжить без токена, но тогда \
                                                          будет доступно гораздо меньше возможностей.\nДля \
                                                         этого напиши "/without_token"')


@dp.message_handler(lambda message: db.get_signup(message.from_user.id) == 'settoken')
async def tkn_setter(message: types.Message):
    if message.text == '/without_token':
        await bot_run.send_message(message.from_user.id, 'Вам доступен функционал, для которого не требуется токен.\nЕсли захотите вести токен, это всегда можно сделать, вызвав команду "/settoken"')
        if db.get_share(message.from_user.id) == []:
            await bot_run.send_message(message.from_user.id, set_shares_message)
        else:
            await bot_run.send_message(message.from_user.id, "Можете изменить выбранные акции с помощью команды /set_shares")
        db.set_sign_up(message.from_user.id, 'done')
        db.set_status(message.from_user.id, "none")
        db.set_token_status(message.from_user.id, "without_token")
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
            db.set_token_status(message.from_user.id, 'choose_acc')
            await bot_run.send_message(message.from_user.id, choose_accounts_message)
            TOKEN = db.get_token(message.from_user.id)
            df = show_accounts(TOKEN)
            await bot_run.send_message(message.from_user.id, df)


@dp.message_handler(lambda message: message.text == '/settoken')
async def status_set_token(message: types.Message):
    db.set_sign_up(message.from_user.id, 'settoken')
    await bot_run.send_message(message.from_user.id,
                           'Введите токен от своего аккаунта Тинькофф Инвестиции\nВы можете продолжить без токена, но тогда будет доступно гораздо меньше возможностей.\nДля этого напиши "/without_token"')


@dp.message_handler(lambda message: db.get_token_status(message.from_user.id) == ['choose_acc'])
async def choose_one_acc(message: types.Message):
    try:
        a = int(message.text)
    except:
        a = "ERROR"
        await bot_run.send_message(message.from_user.id, 'Введите число из предложенных')
    if a != "ERROR":
        TOKEN = db.get_token(message.from_user.id)
        df = show_accounts(TOKEN)

        if a >= len(df['name']):
            await bot_run.send_message(message.from_user.id, 'Слишком большое число')

        else:
            s = df['name'][int(message.text)]
            await bot_run.send_message(message.from_user.id, f'Вы выбрали: {s}')
            if db.get_share(message.from_user.id) == []:
                await bot_run.send_message(message.from_user.id,set_shares_message)
            else:
                await bot_run.send_message(message.from_user.id, "Можете изменить выбранные акции с помощью команды /set_shares")
            query = choose_account(TOKEN, s)
            db.set_token_status(message.from_user.id, f"{list(query[0].items())[0][0]},{list(query[0].items())[0][1]}")



@dp.message_handler(lambda message: message.text == '/set_shares')
async def shares_set(message: types.Message):
    if db.get_share(message.from_user.id) == []:
        await bot_run.send_message(message.from_user.id, 'Пожалуйста, введите через запятую <b>до 10 тикеров</b> (коротких названий на английском языке) ценных бумаг, вы хотите отслеживать у которых Вы желаете отслеживать стоимость:', parse_mode='html')
        await Form.waiting_for_tickers.set()
    else:
        await Form.confirmation.set()
        await bot_run.send_message(message.from_user.id, 'У вас уже есть набор ценных бумаг. Желаете изменить его?')



@dp.message_handler(state=Form.waiting_for_tickers)
async def process_tickers(message: types.Message, state):
    tickers = message.text
    if language_check(tickers) != 3:
        await bot_run.send_message(message.from_user.id, "Недопустимый формат тикеров")
        await Form.waiting_for_tickers.set()
    else:
        tmp_list = tickers.split(",")
        shares_list = []
        for i in tmp_list:
            shares_list.append(i.strip().upper())
        shares, counter = add_shares(shares_list)
        if len(shares_list) >=1 :
            db.set_share(user_id=message.from_user.id, shares_list=shares_list)
            await bot_run.send_message(message.from_user.id, 'Вы удачно изменили набор ценных бумаг!')
            if counter == 1:
                await bot_run.send_message(message.from_user.id,
                                       'Были добавлены не все акции, так как их мы не смогли найти в нашей базе данных')
            await state.finish()

        else:
            await bot_run.send_message(message.from_user.id, 'Таких акций у нас нет, повторите попытку вызвав команду /set_shares')
            await state.finish()


@dp.message_handler(state=Form.confirmation)
async def process_confirmation(message: types.Message, state):
    if message.text.lower() == 'да':
        await Form.waiting_for_tickers.set()
        await bot_run.send_message(message.from_user.id, 'Пожалуйста, введите новый список тикеров (на английском языке, пока нет проверки на русские буквы) через запятую:')
    elif message.text.lower() == 'нет':
        await bot_run.send_message(message.from_user.id, 'Хорошо. Вы можете сделать это в любой момент, если введёте команду /set_shares')
        await state.finish()


@dp.message_handler(lambda message: message.text == "/show_shares")
async def show_shares(message: types.Message):
    result = db.get_share(message.from_user.id)
    await bot_run.send_message(message.from_user.id, result)


@dp.message_handler(lambda message: message.text == "/get_portfolio")
async def get_portfolio(message: types.Message):
    if (db.get_token_status(message.from_user.id) == 'without_token') or db.get_signup(message.from_user.id) != 'done':
        await bot_run.send_message(message.from_user.id, 'Извините, но эта функция не работает без токена. Чтобы установить свой токен, введите команду /settoken.\nУзнать доступные функции можно с помощью команды /help')
    else:
        pdf_out = create_pdf_from_dataframe(df)
        pdf_out.seek(0)
        await bot_run.send_document(message.from_user.id, document=types.InputFile(pdf_out, filename='your_portfolio.pdf'))


@dp.message_handler(lambda message: message.text == "/show_graphics")
async def show_graphics(message: types.message):
    await bot_run.send_message(message.from_user.id, '<a href="https://olblack52-telegramm-chair-com.onrender.com/">Интерактивный график свеч. </a>\nЛучше расположить телефон горизонтально)', parse_mode="html")


@dp.message_handler()
async def smth(message: types.Message):
    if not db.user_exists(message.from_user.id):
        await start_function(message)
    else:
        await bot_run.send_message(message.from_user.id,
                                   'Очень интересно, но ничего не понятно\nЧтобы узнать доступные команды, введите /help')


async def eleven_messages():
    '''
    Эта функция рассылает пользователям информацию о стоимости выбранных ими акций каждый день в 11:00
    '''
    users = db.get_all_users()
    for user_id in users:
        if db.get_share(user_id):
            await bot_run.send_message(user_id, notify_user_about_stocks(user_id=user_id))


async def blm_worker(): 
    ''' 
    Запускается каждые 15 минут и проверяет стоимости акций 
    ''' 
    users = db.get_all_users() 
    for user_id in users: 
        if db.get_share(user_id): 
            if price_checker(user_id=user_id): 
                await bot_run.send_message(user_id, price_checker(user_id=user_id), parse_mode="html")
                
                
if __name__ == "__main__":
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(eleven_messages, trigger="cron", hour=10, minute=59)
    scheduler.add_job(blm_worker, trigger="interval", seconds=1200)
    scheduler.start()
    executor.start_polling(dp, skip_updates=True)


