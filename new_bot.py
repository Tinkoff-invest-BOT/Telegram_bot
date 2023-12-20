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
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


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
def start_function(message):
    '''
    Данная функция обрабатывает сообщение от пользователя,
    который еще не зарегистрирован в системе и добавить его в базу данных
    '''
    db.add_user(message.from_user.id)
    bot_run.send_message(message.from_user.id, start_message)
    bot_run.send_message(message.from_user.id, f'{message.chat.first_name}, выбери себе ник:')
    db.set_sign_up(message.from_user.id, 'setnickname')


@dp.message_handler(commands=['start'])
def start(message: types.Message):
    '''
    Данная функция обрабатывает команду /start и проверяет 
    статус регистрации пользователя в базе данных
    '''
    if not db.user_exists(message.from_user.id):
        start_function(message)
    elif db.get_signup(message.from_user.id) == 'done':
        bot_run.send_message(message.from_user.id, "Вы уже зарегистрированны!")
    else:
        bot_run.send_message(message.from_user.id, 'Продолжайте регистрацию!')


@dp.message_handler(commands=['help'])
def help_function(message: types.Message):
    '''
    Данная функция обрабатывает команду /help и 
    отправляет пользователю информацию о помощи, 
    а затем проверяет статус регистрации
    '''
    bot_run.send_message(message.from_user.id, help_message, parse_mode='html')
    if not db.user_exists(message.from_user.id):
        start(message)
    elif db.get_signup(message.from_user.id) != 'done':
        bot_run.send_message(message.from_user.id, 'Продолжайте регистрацию!')


@dp.message_handler(lambda message: db.get_signup(message.from_user.id) == 'setnickname')
def nick_setter(message: types.Message):
    '''
    Данная функция управляет процессом установки никнейма
    пользователя(проверяет его формат) и переводит
    на следующий этап (установка электронной почты)
    '''
    if len(message.text) > 30:
        bot_run.send_message(message.from_user.id, 'Никнейм не должен превышать 30 символов')
    elif '@' in message.text or '/' in message.text:
        bot_run.send_message(message.from_user.id, 'Вы ввели запрещенный символ')
    else:
        db.set_nickname(message.from_user.id, message.text)
        db.set_sign_up(message.from_user.id, 'setemail')
        bot_run.send_message(message.from_user.id, 'Введите  свой email')


@dp.message_handler(lambda message: db.get_signup(message.from_user.id) == 'setemail')
def mail_setter(message: types.Message):
    '''
    Данная функция обрабатывает сообщения от пользователя, 
    находящегося в состоянии "setemail" в процессе регистрации
    '''
    if len(message.text) < 5:
        bot_run.send_message(message.from_user.id, "Недопустимый email")
    elif '@' not in message.text or '.' not in message.text:
        bot_run.send_message(message.from_user.id, 'Недопустимый формат email')
    else:
        db.set_email(message.from_user.id, message.text)
        db.set_sign_up(message.from_user.id, 'settoken')
        bot_run.send_message(message.from_user.id, 'Введите токен от своего аккаунта Тинькофф <a href="https://developer.tinkoff.ru/docs/intro/manuals/self-service-auth">Как получить токен Tinkoff </a>\
                                                         Инвестиции\nВы можете продолжить без токена, но тогда \
                                                          будет доступно гораздо меньше возможностей.\nДля \
                                                         этого напиши "/without_token"', parse_mode="html")


@dp.message_handler(lambda message: db.get_signup(message.from_user.id) == 'settoken')
def tkn_setter(message: types.Message):
    '''
    Данная функция обрабатывает сообщени от пользователя,
    который находится в состоянии "settoken" в процессе регистрации,
    при этом проверяя наличие сообщения пользователя "without_token"
    '''
    if message.text == '/without_token':
        bot_run.send_message(message.from_user.id, 'Вам доступен функционал, для которого <i>не требуется токен</i>.\nЕсли захотите вести токен, это всегда можно сделать, вызвав команду "/settoken"', parse_mode="html")
        if db.get_share(message.from_user.id) == []:
            bot_run.send_message(message.from_user.id, set_shares_message)
        else:
            bot_run.send_message(message.from_user.id, "Можете изменить выбранные акции с помощью команды /set_shares")
        db.set_sign_up(message.from_user.id, 'done')
        db.set_status(message.from_user.id, "none")
        db.set_token_status(message.from_user.id, "without_token")
    else:
        if token_check(message.text) == 1:
            bot_run.send_message(message.from_user.id, 'Несуществующий токен. Введите токен ещё раз или продолжите без него: /without_token')
        elif token_check(message.text) == 2:
            bot_run.send_message(message.from_user.id,
                                   'Ты когда нибудь видел токен на русском языке? Напиши нормальный токен')
        elif token_check(message.text) == 3:
            bot_run.send_message(message.from_user.id, 'Я такое не понимаю...')

        else:
            db.set_tocken(message.from_user.id, message.text)
            db.set_sign_up(message.from_user.id, 'done')
            db.set_token_status(message.from_user.id, 'choose_acc')
            bot_run.send_message(message.from_user.id, choose_accounts_message)
            TOKEN = db.get_token(message.from_user.id)
            df = show_accounts(TOKEN)
            bot_run.send_message(message.from_user.id, df)


@dp.message_handler(lambda message: message.text == '/settoken')
def status_set_token(message: types.Message):
    db.set_sign_up(message.from_user.id, 'settoken')
    bot_run.send_message(message.from_user.id,
                           'Введите токен от своего аккаунта <b>Тинькофф Инвестиций.</b>\nВы можете продолжить без токена, но тогда будет доступно гораздо меньше возможностей.\nДля этого введите /without_token', parse_mode='html')


@dp.message_handler(lambda message: db.get_token_status(message.from_user.id) == ['choose_acc'])
def choose_one_acc(message: types.Message):
    '''
    Данная функция обрабатывает сообщения от пользователя, находящегося в 
    состоянии выбора счета. Ему предоставляется возможность выбрать
    акции для портфеля, а также изменить выбранные акции. Выбранный счет и 
    связанный с ним токен сохраняются в базе данных 
    '''
    try:
        a = int(message.text)
    except:
        a = "ERROR"
        bot_run.send_message(message.from_user.id, 'Введите число из предложенных')
    if a != "ERROR":
        TOKEN = db.get_token(message.from_user.id)
        df = show_accounts(TOKEN)

        if a >= len(df['name']):
            bot_run.send_message(message.from_user.id, 'Слишком большое число')

        else:
            s = df['name'][int(message.text)]
            bot_run.send_message(message.from_user.id, f'Вы выбрали: {s}')
            if db.get_share(message.from_user.id) == []:
                bot_run.send_message(message.from_user.id,set_shares_message)
            else:
                bot_run.send_message(message.from_user.id, "Можете изменить выбранные акции с помощью команды /set_shares")
            query = choose_account(TOKEN, s)
            db.set_token_status(message.from_user.id, f"{list(query[0].items())[0][0]},{list(query[0].items())[0][1]}")



@dp.message_handler(lambda message: message.text == '/set_shares')
def shares_set(message: types.Message):
    '''
    Данная функция заносит массив тикеров в базу данных
    '''
    if db.get_share(message.from_user.id) == []:
        bot_run.send_message(message.from_user.id, 'Пожалуйста, введите через запятую <b>до 10 тикеров</b> (коротких названий на английском языке) ценных бумаг, вы хотите отслеживать у которых Вы желаете отслеживать стоимость:', parse_mode='html')
        Form.waiting_for_tickers.set()
    else:
        Form.confirmation.set()
        bot_run.send_message(message.from_user.id, 'У вас уже есть набор ценных бумаг. Желаете изменить его?')



@dp.message_handler(state=Form.waiting_for_tickers)
def process_tickers(message: types.Message, state):
    '''
    Данная функция обрабатывает бот вода пользователя,
    связанного с установкой тикеров ценных бумаг, и 
    обновления соответствующих данных в базе данных.
    '''
    tickers = message.text
    if language_check(tickers) != 3:
        bot_run.send_message(message.from_user.id, "Недопустимый формат тикеров")
        Form.waiting_for_tickers.set()
    else:
        tmp_list = tickers.split(",")
        shares_list = []
        for i in tmp_list:
            shares_list.append(i.strip().upper())
        shares, counter = add_shares(shares_list)
        if len(shares_list) >=1 :
            db.set_share(user_id=message.from_user.id, shares_list=shares_list)
            bot_run.send_message(message.from_user.id, 'Вы удачно изменили набор ценных бумаг!')
            if counter == 1:
                bot_run.send_message(message.from_user.id,
                                       'Были добавлены не все акции, так как их мы не смогли найти в нашей базе данных')
            state.finish()

        else:
            bot_run.send_message(message.from_user.id, 'Таких акций у нас нет, повторите попытку вызвав команду /set_shares')
            state.finish()


@dp.message_handler(state=Form.confirmation)
def process_confirmation(message: types.Message, state):
    '''
    Данная функция обрабатывает запрос на ввод нового списка тикеров,
    если того хочет пользователь
    '''
    if message.text.lower() == 'да':
        Form.waiting_for_tickers.set()
        bot_run.send_message(message.from_user.id, 'Пожалуйста, введите новый список тикеров (на английском языке, пока нет проверки на русские буквы) через запятую:')
    elif message.text.lower() == 'нет':
        bot_run.send_message(message.from_user.id, 'Хорошо. Вы можете сделать это в любой момент, если введёте команду /set_shares')
        state.finish()


@dp.message_handler(lambda message: message.text == "/show_shares")
def show_shares(message: types.Message):
    '''
    Данная функция вызывает выбранный пользователем,
    список акций из базы данных
    '''
    result = db.get_share(message.from_user.id)
    bot_run.send_message(message.from_user.id, f"<b>Ваш список любимых акций:</b>\n{', '.join(result)}", parse_mode="html")


@dp.message_handler(lambda message: message.text == "/get_portfolio")
def get_portfolio(message: types.Message):
    '''
    Данная функция вызывает портфель пользователя в виде PDF-документа,
    при этом проверяя регистрацию и наличие токена
    '''
    if (db.get_token_status(message.from_user.id) == 'without_token') or db.get_signup(message.from_user.id) != 'done':
        bot_run.send_message(message.from_user.id, 'Извините, но эта функция не работает без токена. Чтобы установить свой токен, введите команду /settoken.\nУзнать доступные функции можно с помощью команды /help')
    else:
        pdf_out = create_pdf_from_dataframe(df)
        pdf_out.seek(0)
        bot_run.send_document(message.from_user.id, document=types.InputFile(pdf_out, filename='your_portfolio.pdf'))


@dp.message_handler(lambda message: message.text == "/show_graphics")
async def show_graphics(message: types.message):
    '''
    Выводит на сервер график свечей для тикеров,
    выбранных пользователем
    '''
    bot_run.send_message(message.from_user.id, '<a href="https://olblack52-telegramm-chair-com.onrender.com/">Интерактивный график свеч. </a>\nЛучше расположить телефон горизонтально)', parse_mode="html")


@dp.message_handler()
def smth(message: types.Message):
    '''
    Данная функция обрабатывает сообщения пользователя,
    на которые бот не сможет ответить
    '''
    if not db.user_exists(message.from_user.id):
        start_function(message)
    else:
        bot_run.send_message(message.from_user.id,
                                   'Очень интересно, но ничего не понятно\nЧтобы узнать доступные команды, введите /help')

def eleven_messages():
    '''
    Эта функция рассылает пользователям информацию о стоимости выбранных ими акций каждый день в 11:00
    '''
    users = db.get_all_users()
    for user_id in users:
        if db.get_share(user_id):
            bot_run.send_message(user_id, notify_user_about_stocks(user_id=user_id))

def blm_worker(): 
    ''' 
    Запускается каждые 15 минут и проверяет стоимости акций 
    ''' 
    users = db.get_all_users() 
    for user_id in users: 
        if db.get_share(user_id): 
            if price_checker(user_id=user_id): 
                bot_run.send_message(user_id, price_checker(user_id=user_id), parse_mode="html")
                
                
if __name__ == "__main__":
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(eleven_messages, trigger="cron", hour=10, minute=59)
    scheduler.add_job(blm_worker, trigger="interval", seconds=1200)
    scheduler.start()
    executor.start_polling(dp, skip_updates=True)


