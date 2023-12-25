import types

from functions import *
from db import Database
from passwords import *
from connection_db import connection
from messages import *
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot, Dispatcher, executor, types
from parser_daily import notify_user_about_stocks, pct_checker, price_checker
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove


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
    waiting_levels = State()
    ask_if_delete = State()
    waiting_for_share_graph = State()
    waiting_for_book = State()


@dp.message_handler(lambda message: db.user_exists(message.from_user.id) == False)
async def start_function(message):
    '''
    Данная функция обрабатывает сообщение от пользователя,
    который еще не зарегистрирован в системе и добавить его в базу данных
    '''
    db.add_user(message.from_user.id)
    await bot_run.send_message(message.from_user.id, start_message)
    await bot_run.send_message(message.from_user.id, f'{message.chat.first_name}, выбери себе ник:')
    db.set_sign_up(message.from_user.id, 'setnickname')


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    '''
    Данная функция обрабатывает команду /start и проверяет 
    статус регистрации пользователя в базе данных
    '''
    if not db.user_exists(message.from_user.id):
       await start_function(message)
    elif db.get_signup(message.from_user.id) == 'done':
        await bot_run.send_message(message.from_user.id, "Вы уже зарегистрированны!")
    else:
        await bot_run.send_message(message.from_user.id, 'Продолжайте регистрацию!')


@dp.message_handler(commands=['help'])
async def help_function(message: types.Message):
    '''
    Данная функция обрабатывает команду /help и 
    отправляет пользователю информацию о помощи, 
    а затем проверяет статус регистрации
    '''
    await bot_run.send_message(message.from_user.id, help_message, parse_mode='html')
    if not db.user_exists(message.from_user.id):
        await start(message)
    elif db.get_signup(message.from_user.id) != 'done':
        await bot_run.send_message(message.from_user.id, 'Продолжайте регистрацию!')


@dp.message_handler(lambda message: db.get_signup(message.from_user.id) == 'setnickname')
async def nick_setter(message: types.Message):
    '''
    Данная функция управляет процессом установки никнейма
    пользователя(проверяет его формат) и переводит
    на следующий этап (установка электронной почты)
    '''
    if len(message.text) > 30:
        await bot_run.send_message(message.from_user.id, 'Никнейм не должен превышать 30 символов')
    elif '@' in message.text or '/' in message.text:
        await bot_run.send_message(message.from_user.id, 'Вы ввели запрещенный символ')
    else:
        db.set_nickname(message.from_user.id, message.text)
        db.set_sign_up(message.from_user.id, 'setemail')
        await bot_run.send_message(message.from_user.id, 'Введите свой email')


@dp.message_handler(lambda message: db.get_signup(message.from_user.id) == 'setemail')
async def mail_setter(message: types.Message):
    '''
    Данная функция обрабатывает сообщения от пользователя, 
    находящегося в состоянии "setemail" в процессе регистрации
    '''
    if len(message.text) < 5:
        await bot_run.send_message(message.from_user.id, "Недопустимый email")
    elif '@' not in message.text or '.' not in message.text:
        await bot_run.send_message(message.from_user.id, 'Недопустимый формат email')
    else:
        db.set_email(message.from_user.id, message.text)
        db.set_sign_up(message.from_user.id, 'settoken')
        await bot_run.send_message(message.from_user.id, set_token_message, parse_mode="html")


@dp.message_handler(lambda message: db.get_signup(message.from_user.id) == 'settoken')
async def tkn_setter(message: types.Message):
    '''
    Данная функция обрабатывает сообщени от пользователя,
    который находится в состоянии "settoken" в процессе регистрации,
    при этом проверяя наличие сообщения пользователя "without_token"
    '''
    if message.text == '/without_token':
        await bot_run.send_message(message.from_user.id, 'Вам доступен функционал, для которого <i>не требуется токен</i>.\nЕсли захотите вести токен, это всегда можно сделать, вызвав команду "/settoken"', parse_mode="html")
        if db.get_share(message.from_user.id) == []:
            await bot_run.send_message(message.from_user.id, set_shares_message)
        else:
            await bot_run.send_message(message.from_user.id, "Можете изменить выбранные акции с помощью команды /set_shares")
        db.set_sign_up(message.from_user.id, 'done')
        db.set_status(message.from_user.id, "none")
        db.set_token_status(message.from_user.id, "without_token")
    else:
        if token_check(message.text) == 1:
            await bot_run.send_message(message.from_user.id, 'Несуществующий токен. Введите токен ещё раз или продолжите без него: /without_token')
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
                           'Введите токен от своего аккаунта <b>Тинькофф Инвестиций.</b>\nВы можете продолжить без токена, но тогда будет доступно гораздо меньше возможностей.\nДля этого введите /without_token', parse_mode='html')


@dp.message_handler(lambda message: db.get_token_status(message.from_user.id) == ['choose_acc'])
async def choose_one_acc(message: types.Message):
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


@dp.message_handler(lambda message: message.text == '/get_book')
async def book(message:types.Message):
    TOKEN = db.get_token(message.from_user.id)
    if TOKEN is None:
        await bot_run.send_message(message.from_user.id, "Функция доступна только авторизированным пользователям")
    else:
        await bot_run.send_message(message.from_user.id, "Пожалуйста введите тикер акции")
        await Form.waiting_for_book.set()


@dp.message_handler(state=Form.waiting_for_book)
async def booking(message:types.Message, state):
    query = message.text
    if not share_check(query):
        await bot_run.send_message(message.from_user.id, exeptions['3'])
        await state.finish()
    TOKEN = db.get_token(message.from_user.id)
    figi = db.ticker_to_figi(query)
    result = get_glass(figi=figi, TOKEN=TOKEN)
    if type(result) is str:
        await bot_run.send_message(message.from_user.id, result)
        await state.finish()
    elif result == 30079:
        await bot_run.send_message(message.from_user.id, exeptions['30079'])
        await state.finish()
    else:
        await bot_run.send_message(message.from_user.id, exeptions['1'])
        await state.finish()




@dp.message_handler(lambda message: message.text == '/set_shares')
async def shares_set(message: types.Message):
    '''
    Данная функция заносит массив тикеров в базу данных
    '''
    if db.get_share(message.from_user.id) == []:
        await bot_run.send_message(message.from_user.id, 'Пожалуйста, введите через запятую <b>до 10 тикеров</b> (коротких названий на английском языке) ценных бумаг, вы хотите отслеживать у которых Вы желаете отслеживать стоимость:', parse_mode='html')
        await Form.waiting_for_tickers.set()
    else:
        await Form.confirmation.set()
        await bot_run.send_message(message.from_user.id, 'У вас уже есть набор ценных бумаг. Желаете изменить его?')



@dp.message_handler(state=Form.waiting_for_tickers)
async def process_tickers(message: types.Message, state):
    '''
    Данная функция обрабатывает бот вода пользователя,
    связанного с установкой тикеров ценных бумаг, и 
    обновления соответствующих данных в базе данных.
    '''
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
    '''
    Данная функция обрабатывает запрос на ввод нового списка тикеров,
    если того хочет пользователь
    '''
    if message.text.lower() == 'да':
        await Form.waiting_for_tickers.set()
        await bot_run.send_message(message.from_user.id, 'Пожалуйста, введите новый список тикеров (на английском языке, пока нет проверки на русские буквы) через запятую:')
    elif message.text.lower() == 'нет':
        await bot_run.send_message(message.from_user.id, 'Хорошо. Вы можете сделать это в любой момент, если введёте команду /set_shares')
        await state.finish()


@dp.message_handler(lambda message: message.text == "/show_shares")
async def show_shares(message: types.Message):
    '''
    Данная функция вызывает выбранный пользователем,
    список акций из базы данных
    '''
    result = db.get_share(message.from_user.id)
    await bot_run.send_message(message.from_user.id, f"<b>Ваш список любимых акций:</b>\n{', '.join(result)}", parse_mode="html")


@dp.message_handler(lambda message: message.text == "/get_portfolio")
async def get_portfolio(message: types.Message):
    '''
    Данная функция вызывает портфель пользователя в виде PDF-документа,
    при этом проверяя регистрацию и наличие токена
    '''
    if (db.get_token_status(message.from_user.id) == 'without_token') or db.get_signup(message.from_user.id) != 'done':
        await bot_run.send_message(message.from_user.id, 'Извините, но эта функция не работает без токена. Чтобы установить свой токен, введите команду /settoken.\nУзнать доступные функции можно с помощью команды /help')
    else:
        result = get_portfolio_(message.from_user.id)
        if type(result) is pd.core.frame.DataFrame:
            pdf_out = create_pdf_from_dataframe(result)
            pdf_out.seek(0)
            await bot_run.send_document(message.from_user.id, document=types.InputFile(pdf_out, filename='your_portfolio.pdf'))
        else:
            try:
                err = exeptions[result]
            except:
                err = result
            await bot_run.send_message(message.from_user.id, err)



@dp.message_handler(lambda message: message.text == "/show_graphics")
async def show_graphics(message: types.message):
    '''
    Выводит на сервер график свечей для тикеров,
    выбранных пользователем
    '''
    await bot_run.send_message(message.from_user.id, '<a href="https://alblack52-telegramm-com.onrender.com">Интерактивный график свеч. </a>\nЛучше расположить телефон горизонтально)', parse_mode="html")


@dp.message_handler(lambda message: message.text == "/operations")
async def operations_start(message:types.Message):
    '''
    Функция для операций с ценными бумагами
    '''
    db.set_status(message.from_user.id, 'operations')
    await bot_run.send_message(message.from_user.id, operation_message)


@dp.message_handler(lambda message: db.get_status(message.from_user.id) == 'operations')
async def operations(message: types.Message):
    query = message.text
    try:
        a = int(query)
    except:
        a = "ERROR"
        db.set_status(message.from_user.id, "none")
        await bot_run.send_message(message.from_user.id, 'Нужно выбрать цифру из предложенных.\nОперация прервана, введите /operations что-бы начать заново')
    if a != "ERROR":
        if int(query) == 1:
            db.set_status(message.from_user.id, 'buying_m')
            await bot_run.send_message(message.from_user.id, buying_message_m, parse_mode = "html")
        elif int(query) == 2:
            db.set_status(message.from_user.id, "selling_m")
            await bot_run.send_message(message.from_user.id, selling_message_m, parse_mode = "html")
        elif int(query) == 3:
            db.set_status(message.from_user.id, "buying_l")
            await bot_run.send_message(message.from_user.id, buying_message_l, parse_mode = "html")
        elif int(query) == 4:
            db.set_status(message.from_user.id, "selling_l")
            await bot_run.send_message(message.from_user.id, selling_message_l, parse_mode = "html")
        else:
            db.set_status(message.from_user.id, "none")
            await bot_run.send_message(message.from_user.id, 'Нужно выбрать цифру из предложенных.\nОперация прервана, введите \operations что-бы начать заново')


@dp.message_handler(lambda message: db.get_status(message.from_user.id) == 'buying_m')
async def buying(message:types.Message):
    try:
        query = message.text
        st = query.split(' ')
        n_query = []
        for i in st:
            n_query.append(i.strip())
        n_query[0] = n_query[0].upper()
        if len(n_query) == 2:
            n_query.append('best_price')
    except:
        await bot_run.send_message(message.from_user.id, "Неверный запрос")
        db.set_status(message.from_user.id, "none")
        return

    try:
        a = before_buying_market(message.from_user.id, n_query[0], int(n_query[1]), n_query[2])
        if type(a) is str:
            try:
                ans = exeptions[a]
            except:
                ans = "Произошла ошибка"
        else:
            ans = "Успешно!"

        await bot_run.send_message(message.from_user.id, ans)
        db.set_status(message.from_user.id, "none")
    except:
        await bot_run.send_message(message.from_user.id, "Произошла ошибка, попробуйте снова")
        db.set_status(message.from_user.id, "none")


@dp.message_handler(lambda message: db.get_status(message.from_user.id) == 'selling_m')
async def buying(message:types.Message):
    try:
        query = message.text
        st = query.split(' ')
        n_query = []
        for i in st:
            n_query.append(i.strip())
        n_query[0] = n_query[0].upper()
        if len(n_query) == 2:
            n_query.append('best_price')
    except:
        await bot_run.send_message(message.from_user.id, "Неверный запрос")
        db.set_status(message.from_user.id, "none")
        return

    try:
        a = before_selling_market(message.from_user.id, n_query[0], int(n_query[1]), n_query[2])
        if type(a) is str:
            try:
                ans = exeptions[a]
            except:
                ans = "Произошла ошибка"
        else:
            ans = "Успешно!"
        await bot_run.send_message(message.from_user.id, ans)
        db.set_status(message.from_user.id, "none")
    except Exception as e:
        await bot_run.send_message(message.from_user.id, str(e))
        db.set_status(message.from_user.id, "none")


@dp.message_handler(lambda message: db.get_status(message.from_user.id) == 'buying_l')
async def buying(message:types.Message):
    query = message.text
    try:
        st = query.split(' ')
        n_query = []
        for i in st:
            n_query.append(i.strip())
        n_query[0] = n_query[0].upper()
        if len(n_query) != 3:
            await bot_run.send_message(message.from_user.id, "Неверный запрос")
            db.set_status(message.from_user.id, "none")
    except:
        await bot_run.send_message(message.from_user.id, "Неверный запрос")
        db.set_status(message.from_user.id, "none")
        return

    try:
        a = before_buying_limit(message.from_user.id, n_query[0], int(n_query[1]), n_query[2])
        if type(a) is str:
            try:
                ans = exeptions[a]
            except:
                ans = "Произошла ошибка"
        else:
            ans = "Успешно!"
        await bot_run.send_message(message.from_user.id, ans)
        db.set_status(message.from_user.id, "none")
    except Exception as e:
        await bot_run.send_message(message.from_user.id, str(e))
        db.set_status(message.from_user.id, "none")


@dp.message_handler(lambda message: db.get_status(message.from_user.id) == 'selling_l')
async def buying(message: types.Message):
    query = message.text
    try:
        st = query.split(' ')
        n_query = []
        for i in st:
            n_query.append(i.strip())
        n_query[0] = n_query[0].upper()
        if len(n_query) != 3:
            await bot_run.send_message(message.from_user.id, "Неверный запрос")
            db.set_status(message.from_user.id, "none")
    except:
        await bot_run.send_message(message.from_user.id, "Неверный запрос")
        db.set_status(message.from_user.id, "none")
        return

    try:
        a = before_selling_limit(message.from_user.id, n_query[0], int(n_query[1]), n_query[2])
        if type(a) is str:
            try:
                ans = exeptions[a]
            except:
                ans = "Произошла ошибка"
        else:
            ans = "Успешно!"
        await bot_run.send_message(message.from_user.id, ans)
        db.set_status(message.from_user.id, "none")
    except Exception as e:
        await bot_run.send_message(message.from_user.id, str(e))
        db.set_status(message.from_user.id, "none")


@dp.message_handler(lambda message: message.text == "/change_account")
async def change_account(message: types.Message):
    if db.get_token(user_id=message.from_user.id) is not None:
        db.set_token_status(message.from_user.id, 'choose_acc')
        await bot_run.send_message(message.from_user.id, choose_accounts_message)
        TOKEN = db.get_token(message.from_user.id)
        df = show_accounts(TOKEN)
        await bot_run.send_message(message.from_user.id, df)
    else:
        await bot_run.send_message(message.from_user.id, "Выбор аккаунта доступен только пользователям с Токеном")


@dp.message_handler(lambda message: message.text == "/set_level_price")
async def show_graphics(message: types.message):
    await bot_run.send_message(message.from_user.id, set_price_level, parse_mode="html")
    await Form.waiting_levels.set()


@dp.message_handler(state=Form.waiting_levels)
async def levels_set(message: types.Message, state):
    text = message.text
    if text == '/cancel':
        await bot_run.send_message(message.from_user.id, cancelling, parse_mode="html")
        await state.finish()
    else:
        text = text.split()
        shares_list, flag = add_shares([text[0]])
        if flag != 0:
            await bot_run.send_message(message.from_user.id, "Недопустимый формат тикеров или мы не нашли его в нашей базе данных(")
            await Form.waiting_levels.set()
        else:
            db.set_levels(message.from_user.id, text)
            await bot_run.send_message(message.from_user.id, f"Вы теперь следители за стоимостью акций {text[0]}")
            await state.finish()


@dp.message_handler(commands=['delete'])
async def delete_user(message: types.Message):
    '''
    Данная функция обрабатывает команду /delete и 
    удаляет пользователя из базы данных
    '''
    mark_up = ReplyKeyboardMarkup(resize_keyboard=True)
    mark_up.add(KeyboardButton('Да'))
    mark_up.add(KeyboardButton('Нет'))
    user_id = message.from_user.id
    await bot_run.send_message(user_id, 'Вы точно хотите удалить профиль?', reply_markup=mark_up)
    await Form.ask_if_delete.set()


@dp.message_handler(state=Form.ask_if_delete)
async def answer_id_delete(message: types.Message, state):
    user_id = message.from_user.id
    if message.text.lower() == 'да':
        db.delete_user(user_id)
        await bot_run.send_message(user_id, 'Ваш профиль успешно удален.', reply_markup=ReplyKeyboardRemove())
        await state.finish()
    elif message.text.lower() == 'нет':
        await bot_run.send_message(user_id, 'Мы очень рады, что вы остались.', reply_markup=ReplyKeyboardRemove())
        await state.finish()
    else:
        await bot_run.send_message(user_id, 'Непонятный запрос, повторите.')


@dp.message_handler(lambda message: message.text == "/send_share_graph")
async def send_share_graph(message : types.Message):
    await bot_run.send_message(message.from_user.id, "Введите тикер акции, чей график хотите увидеть:", parse_mode="html")
    await Form.waiting_for_share_graph.set()


@dp.message_handler(state=Form.waiting_for_share_graph)
async def answer_id_delete(message: types.Message, state):
    text = message.text
    if text == '/cancel':
        await bot_run.send_message(message.from_user.id, cancelling, parse_mode="html")
        await state.finish()
    else:
        shares_list, flag = add_shares([text])
        if flag != 0:
            await bot_run.send_message(message.from_user.id, "Недопустимый формат тикеров или мы не нашли его в нашей базе данных(")
            await Form.waiting_levels.set()
        else:
            image_base64 = photo_generating(ticker=text)
            image_bytes = base64.b64decode(image_base64)
            image_file = BytesIO(image_bytes)
            image_file.name = 'graph.png'
            await bot_run.send_photo(message.from_user.id, photo=image_file)
            await state.finish()


@dp.message_handler()
async def smth(message: types.Message):
    '''
    Данная функция обрабатывает сообщения пользователя,
    на которые бот не сможет ответить
    '''
    if not db.user_exists(message.from_user.id):
        await start_function(message)
    else:
        msg = await bot_run.send_message(message.from_user.id,
                                   'Очень интересно, но ничего не понятно\nЧтобы узнать доступные команды, введите /help')
        await beautiful_messages(message.from_user.id, "Я такое не понимаю ...", msg)
        await bot_run.send_message(message.from_user.id,
                                         'Чтобы узнать доступные команды, введите /help')



async def beautiful_messages(user_id, message, msg):
    s = ''
    for ch in message:
        r = '}'
        while r != ch:
            r = chr(randint(65,122))
            if random() > 0.5:
                r = ch
            try:
                await bot_run.edit_message_text(s + r, user_id, msg.message_id)
            except:
                pass
        s+=r


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
    Запускается каждые 15 минут и проверяет стоимости акций (процент)
    ''' 
    users = db.get_all_users() 
    for user_id in users: 
        if db.get_share(user_id): 
            message = pct_checker(user_id=user_id)
            if message: 
                await bot_run.send_message(user_id, message, parse_mode="html")
                

async def wlm_worker():
    '''
    Запускается каждую минуту секунд и проверяет уровни акций для каждого пользователя
    '''
    users = db.get_all_users()
    for user_id in users:
        if db.get_levels(user_id=user_id):
            message = price_checker(user_id=user_id)
            if message:
                await bot_run.send_message(user_id, message, parse_mode="html")
                
                
if __name__ == "__main__":
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(eleven_messages, trigger="cron", hour=10, minute=59)
    scheduler.add_job(blm_worker, trigger="interval", seconds=900)
    scheduler.add_job(wlm_worker, trigger="interval", seconds=60)
    scheduler.start()
    executor.start_polling(dp, skip_updates=True)
