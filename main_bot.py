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
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
import markups
import datetime
from dateutil.parser import parse
from analyzer import Analyzer


logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
bot_run = Bot('6742219478:AAGNPdgXSdzYPdbOkHFt6yvo6417aqm68qE')
dp = Dispatcher(bot_run, storage=storage)
db = Database(connection)


class Form(StatesGroup):
    '''
    Этот класс нужен для того, чтобы запоминать состояние разговора с пользователем
    '''
    set_nickname = State()
    set_email = State()
    set_token = State()
    choose_acc = State()
    main_menu = State()
    waiting_for_tickers = State()
    confirmation = State()
    waiting_levels = State()
    ask_if_delete = State()
    operations = State()
    buying_m = State()
    selling_m = State()
    buying_l = State()
    selling_l = State()
    analyzer_tickers = State()
    analyzer_date = State()
    analyzer_finish = State()
    

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    '''
    Данная функция обрабатывает команду /start и проверяет 
    статус регистрации пользователя в базе данных
    '''
    if db.user_exists(message.from_user.id):
       db.delete_user(message.from_user.id)
    db.add_user(message.from_user.id)
    await bot_run.send_message(message.from_user.id, start_message, reply_markup=ReplyKeyboardRemove())
    await bot_run.send_message(message.from_user.id, f'{message.chat.first_name}, выбери себе ник:')
    await Form.set_nickname.set()
    db.set_sign_up(message.from_user.id, 'setnickname')
    

@dp.message_handler(state=Form.set_nickname)
async def nick_setter(message: types.Message, state):
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
        await state.finish()
        await Form.set_email.set()
        await bot_run.send_message(message.from_user.id, 'Введите свой email')
        
        
@dp.message_handler(state=Form.set_email)
async def mail_setter(message: types.Message, state):
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
        await state.finish()
        await Form.set_token.set()
        await bot_run.send_message(message.from_user.id, set_token_message, parse_mode="html", reply_markup=markups.without_token)
        
        
@dp.message_handler(state=Form.set_token)
async def tkn_setter(message: types.Message, state):
    '''
    Данная функция обрабатывает сообщени от пользователя,
    который находится в состоянии "settoken" в процессе регистрации,
    при этом проверяя наличие сообщения пользователя "without_token"
    '''
    if message.text == 'Without token':
        await bot_run.send_message(message.from_user.id, 'Вам доступен функционал, для которого <i>не требуется токен</i>.\nЕсли захотите вести токен, это всегда можно сделать, вызвав команду "/settoken"', parse_mode="html")
        await bot_run.send_message(message.from_user.id, set_shares_message)
        await bot_run.send_message(message.from_user.id, "Вы перенаправлены в главное меню.", reply_markup=markups.main_menu)
        db.set_sign_up(message.from_user.id, 'done')
        db.set_status(message.from_user.id, "none")
        db.set_token_status(message.from_user.id, "without_token")
        await state.finish()
        await Form.main_menu.set()
    else:
        if token_check(message.text) == 1:
            await bot_run.send_message(message.from_user.id, 'Несуществующий токен. Введите токен ещё раз или продолжите без него: "Without token"')
        elif token_check(message.text) == 2:
            await bot_run.send_message(message.from_user.id,
                                   'Ты когда нибудь видел токен на русском языке? Напиши нормальный токен')
        elif token_check(message.text) == 3:
            await bot_run.send_message(message.from_user.id, 'Я такое не понимаю...')

        else:
            db.set_tocken(message.from_user.id, message.text)
            db.set_sign_up(message.from_user.id, 'done')
            db.set_token_status(message.from_user.id, 'choose_acc')
            await state.finish()
            await Form.choose_acc.set()
            await bot_run.send_message(message.from_user.id, choose_accounts_message, reply_markup=ReplyKeyboardRemove())
            TOKEN = db.get_token(message.from_user.id)
            df = show_accounts(TOKEN)
            await bot_run.send_message(message.from_user.id, df)
            
            
@dp.message_handler(state=Form.choose_acc)
async def choose_one_acc(message: types.Message, state):
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
            await bot_run.send_message(message.from_user.id, set_shares_message)
            await bot_run.send_message(message.from_user.id, "Вы перенаправлены в главное меню.", reply_markup=markups.main_menu)
            query = choose_account(TOKEN, s)
            db.set_token_status(message.from_user.id, f"{list(query[0].items())[0][0]},{list(query[0].items())[0][1]}")
            await state.finish()
            await Form.main_menu.set()
    
    
@dp.message_handler(state=Form.main_menu, commands=['help'])
async def help_function(message: types.Message, state):
    '''
    Данная функция обрабатывает команду /help и 
    отправляет пользователю информацию о помощи
    '''
    await bot_run.send_message(message.from_user.id, help_message, parse_mode='html')
    
    
@dp.message_handler(state=Form.main_menu, commands=['settoken'])
async def status_set_token(message: types.Message, state):
    db.set_sign_up(message.from_user.id, 'settoken')
    await state.finish()
    await Form.set_token.set()
    await bot_run.send_message(message.from_user.id,
                           'Введите токен от своего аккаунта <b>Тинькофф Инвестиций.</b>\nВы можете продолжить без токена, но тогда будет доступно гораздо меньше возможностей.\nДля этого введите "Without token"',
                           parse_mode='html',
                           reply_markup=markups.without_token)
    
    
@dp.message_handler(state=Form.main_menu, commands=['set_shares'])
async def shares_set(message: types.Message, state):
    '''
    Данная функция заносит массив тикеров в базу данных
    '''
    if db.get_share(message.from_user.id) == []:
        await bot_run.send_message(message.from_user.id, 'Пожалуйста, введите через запятую <b>до 10 тикеров</b> (коротких названий на английском языке) ценных бумаг, вы хотите отслеживать у которых Вы желаете отслеживать стоимость:',
                                   parse_mode='html',
                                   reply_markup=markups.to_main_menu)
        await state.finish()
        await Form.waiting_for_tickers.set()
    else:
        await state.finish()
        await Form.confirmation.set()
        await bot_run.send_message(message.from_user.id,
                                   'У вас уже есть набор ценных бумаг. Желаете изменить его?',
                                   reply_markup=markups.yes_no)
        
        
@dp.message_handler(state=Form.confirmation)
async def process_confirmation(message: types.Message, state):
    '''
    Данная функция обрабатывает запрос на ввод нового списка тикеров,
    если того хочет пользователь
    '''
    if message.text == 'Да' or message.text == 'да':
        await state.finish()
        await Form.waiting_for_tickers.set()
        await bot_run.send_message(message.from_user.id, 'Пожалуйста, введите новый список тикеров (на английском языке, пока нет проверки на русские буквы) через запятую:',
                                   reply_markup=markups.to_main_menu)
    elif message.text == 'Нет' or message.text == 'нет':
        await bot_run.send_message(message.from_user.id, 'Хорошо. Вы можете сделать это в любой момент, если введёте команду /set_shares в главном меню.\nВы перенаправлены в главное меню.',
                                   reply_markup=markups.main_menu)
        await state.finish()
        await Form.main_menu.set()
    else:
        await bot_run.send_message(message.from_user.id, 'Непонятный ввод. Вы желаете изменить набор ценных бумаг? (Да или нет)')
        
        
@dp.message_handler(state=Form.waiting_for_tickers)
async def process_tickers(message: types.Message, state):
    '''
    Данная функция обрабатывает бот вода пользователя,
    связанного с установкой тикеров ценных бумаг, и 
    обновления соответствующих данных в базе данных.
    '''
    tickers = message.text
    if tickers == "В главное меню":
        await bot_run.send_message(message.from_user.id, "Возврат в главное меню.",
                                   reply_markup=markups.main_menu)
        await state.finish()
        await Form.main_menu.set()
        return
    if language_check(tickers) != 3:
        await bot_run.send_message(message.from_user.id, "Недопустимый формат тикеров. Введите еще раз.")
    else:
        tmp_list = tickers.split(",")
        shares_list = []
        for i in tmp_list:
            shares_list.append(i.strip().upper())
        for i in shares_list:
            if ' ' in i:
                await bot_run.send_message(message.from_user.id,
                                           "Тикеры надо вводить <b>через запятую</b>. Введите еще раз.",
                                           parse_mode='html')
                return
        shares, counter = add_shares(shares_list)
        if len(shares_list) >=1 :
            db.set_share(user_id=message.from_user.id, shares_list=shares_list)
            await bot_run.send_message(message.from_user.id, 'Вы удачно изменили набор ценных бумаг!\nВы перенаправлены в главное меню.',
                                       reply_markup=markups.main_menu)
            if counter == 1:
                await bot_run.send_message(message.from_user.id,
                                       'Были добавлены не все акции, так как их мы не смогли найти в нашей базе данных')
            await state.finish()
            await Form.main_menu.set()

        else:
            await bot_run.send_message(message.from_user.id, 'Таких акций у нас нет, повторите попытку.')
            
            
@dp.message_handler(state=Form.main_menu, commands=["show_shares"])
async def show_shares(message: types.Message, state):
    '''
    Данная функция вызывает выбранный пользователем,
    список акций из базы данных
    '''
    result = db.get_share(message.from_user.id)
    await bot_run.send_message(message.from_user.id, f"<b>Ваш список любимых акций:</b>\n{', '.join(result)}", parse_mode="html")
    
    
@dp.message_handler(state=Form.main_menu, commands=["get_portfolio"])
async def get_portfolio(message: types.Message, state):
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
            
            
@dp.message_handler(state=Form.main_menu, commands=["show_graphics"])
async def show_graphics(message: types.message, state):
    '''
    Выводит на сервер график свечей для тикеров,
    выбранных пользователем
    '''
    await bot_run.send_message(message.from_user.id, '<a href="https://alblack52-telegramm-com.onrender.com">Интерактивный график свеч. </a>\nЛучше расположить телефон горизонтально)', parse_mode="html")
    
    
@dp.message_handler(state=Form.main_menu, commands=["operations"])
async def operations_start(message:types.Message, state):
    '''
    Функция для операций с ценными бумагами
    '''
    db.set_status(message.from_user.id, 'operations')
    await state.finish()
    await Form.operations.set()
    await bot_run.send_message(message.from_user.id, 'hi', reply_markup=markups.operations)
    
    
@dp.message_handler(state=Form.operations)
async def operations(message: types.Message, state):
    query = message.text
    if query == "В главное меню":
        await bot_run.send_message(message.from_user.id, "Возврат в главное меню.", reply_markup=markups.main_menu)
        await state.finish()
        await Form.main_menu.set()
        db.set_status(message.from_user.id, "none")
        return
    if query in ['1', '2', '3', '4']:
        if int(query) == 1:
            db.set_status(message.from_user.id, 'buying_m')
            await state.finish()
            await Form.buying_m.set()
            await bot_run.send_message(message.from_user.id, buying_message_m, parse_mode = "html", reply_markup=markups.to_main_menu)
        elif int(query) == 2:
            db.set_status(message.from_user.id, "selling_m")
            await state.finish()
            await Form.selling_m.set()
            await bot_run.send_message(message.from_user.id, selling_message_m, parse_mode = "html", reply_markup=markups.to_main_menu)
        elif int(query) == 3:
            db.set_status(message.from_user.id, "buying_l")
            await state.finish()
            await Form.buying_l.set()
            await bot_run.send_message(message.from_user.id, buying_message_l, parse_mode = "html", reply_markup=markups.to_main_menu)
        elif int(query) == 4:
            db.set_status(message.from_user.id, "selling_l")
            await state.finish()
            await Form.selling_l.set()
            await bot_run.send_message(message.from_user.id, selling_message_l, parse_mode = "html", reply_markup=markups.to_main_menu)
    else:
        await bot_run.send_message(message.from_user.id, 'Нужно выбрать цифру из предложенных.\nПовторите запрос.')
        
        
@dp.message_handler(state=Form.buying_m)
async def buying(message:types.Message, state):
    if message.text == "В главное меню":
        await bot_run.send_message(message.from_user.id, "Возврат в главное меню.", reply_markup=markups.main_menu)
        await state.finish()
        await Form.main_menu.set()
        db.set_status(message.from_user.id, "none")
        return
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
        await bot_run.send_message(message.from_user.id, "Неверный запрос. Повторите попытку.")
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
        await bot_run.send_message(message.from_user.id, ans + '\nВы перенаправлены в главное меню.', reply_markup=markups.main_menu)
        await state.finish()
        await Form.main_menu.set()
        db.set_status(message.from_user.id, "none")
    except Exception as e:
        await bot_run.send_message(message.from_user.id, f"Произошла ошибка: {str(e)}\nВы перенаправлены в главое меню.", reply_markup=markups.main_menu)
        await state.finish()
        await Form.main_menu.set()
        db.set_status(message.from_user.id, "none")
        
        
@dp.message_handler(state=Form.selling_m)
async def buying(message:types.Message, state):
    if message.text == "В главное меню":
        await bot_run.send_message(message.from_user.id, "Возврат в главное меню.", reply_markup=markups.main_menu)
        await state.finish()
        await Form.main_menu.set()
        db.set_status(message.from_user.id, "none")
        return
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
        await bot_run.send_message(message.from_user.id, "Неверный запрос. Повторите попытку.")
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
        
        await bot_run.send_message(message.from_user.id, ans + '\nВы перенаправлены в главное меню.', reply_markup=markups.main_menu)
        await state.finish()
        await Form.main_menu.set()
        db.set_status(message.from_user.id, "none")
    except Exception as e:
        await bot_run.send_message(message.from_user.id, f"Произошла ошибка: {str(e)}\nВы перенаправлены в главое меню.", reply_markup=markups.main_menu)
        await state.finish()
        await Form.main_menu.set()
        db.set_status(message.from_user.id, "none")
        
        
@dp.message_handler(state=Form.buying_l)
async def buying(message:types.Message, state):
    if message.text == "В главное меню":
        await bot_run.send_message(message.from_user.id, "Возврат в главное меню.", reply_markup=markups.main_menu)
        await state.finish()
        await Form.main_menu.set()
        db.set_status(message.from_user.id, "none")
        return
    query = message.text
    try:
        st = query.split(' ')
        n_query = []
        for i in st:
            n_query.append(i.strip())
        n_query[0] = n_query[0].upper()
        if len(n_query) != 3:
            await bot_run.send_message(message.from_user.id, "Неверный запрос. Повторите попытку.")
            return
    except:
        await bot_run.send_message(message.from_user.id, "Неверный запрос. Повторите попытку.")
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
        await bot_run.send_message(message.from_user.id, ans + '\nВы перенаправлены в главное меню.', reply_markup=markups.main_menu)
        await state.finish()
        await Form.main_menu.set()
        db.set_status(message.from_user.id, "none")
    except Exception as e:
        await bot_run.send_message(message.from_user.id, f"Произошла ошибка: {str(e)}\nВы перенаправлены в главное меню.", reply_markup=markups.main_menu)
        await state.finish()
        await Form.main_menu.set()
        db.set_status(message.from_user.id, "none")


@dp.message_handler(state=Form.selling_l)
async def buying(message: types.Message, state):
    if message.text == "В главное меню":
        await bot_run.send_message(message.from_user.id, "Возврат в главное меню.", reply_markup=markups.main_menu)
        await state.finish()
        await Form.main_menu.set()
        db.set_status(message.from_user.id, "none")
        return
    query = message.text
    try:
        st = query.split(' ')
        n_query = []
        for i in st:
            n_query.append(i.strip())
        n_query[0] = n_query[0].upper()
        if len(n_query) != 3:
            await bot_run.send_message(message.from_user.id, "Неверный запрос. Повторите попытку.")
            return
    except:
        await bot_run.send_message(message.from_user.id, "Неверный запрос. Повторите попытку.")
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
        await bot_run.send_message(message.from_user.id, ans + '\nВы перенаправлены в главное меню.', reply_markup=markups.main_menu)
        await state.finish()
        await Form.main_menu.set()
        db.set_status(message.from_user.id, "none")
    except Exception as e:
        await bot_run.send_message(message.from_user.id, f"Произошла ошибка: {str(e)}\nВы перенаправлены в главое меню.", reply_markup=markups.main_menu)
        await state.finish()
        await Form.main_menu.set()
        db.set_status(message.from_user.id, "none")
        
        
@dp.message_handler(state=Form.main_menu, commands=["change_account"])
async def change_account(message: types.Message, state):
    if db.get_token(user_id=message.from_user.id) is not None:
        db.set_token_status(message.from_user.id, 'choose_acc')
        await state.finish()
        await Form.choose_acc.set()
        await bot_run.send_message(message.from_user.id, choose_accounts_message, reply_markup=ReplyKeyboardRemove())
        TOKEN = db.get_token(message.from_user.id)
        df = show_accounts(TOKEN)
        await bot_run.send_message(message.from_user.id, df)
    else:
        await bot_run.send_message(message.from_user.id, "Выбор аккаунта доступен только пользователям с Токеном")
        
        
@dp.message_handler(state=Form.main_menu, commands=["set_level_price"])
async def show_graphics(message: types.message, state):
    await bot_run.send_message(message.from_user.id, set_price_level, parse_mode="html", reply_markup=markups.to_main_menu)
    await state.finish()
    await Form.waiting_levels.set()
    
    
@dp.message_handler(state=Form.waiting_levels)
async def levels_set(message: types.Message, state):
    text = message.text
    if text == 'В главное меню':
        await bot_run.send_message(message.from_user.id, "Возврат в главное меню.",
                                   parse_mode="html", reply_markup=markups.main_menu)
        await state.finish()
        await Form.main_menu.set()
    else:
        text = text.split()
        shares_list, flag = add_shares([text[0]])
        if flag != 0:
            await bot_run.send_message(message.from_user.id,
                                       "Недопустимый формат тикеров или мы не нашли его в нашей базе данных(\nПовторите запрос.")
        else:
            db.set_levels(message.from_user.id, text)
            await bot_run.send_message(message.from_user.id,
                                       f"Вы теперь отслеживаете стоимость акций {text[0]}\nВы перенаправлены в главное меню.",
                                       reply_markup=markups.main_menu)
            await state.finish()
            await Form.main_menu.set()
            
            
@dp.message_handler(state=Form.main_menu, commands=['delete'])
async def delete_user(message: types.Message, state):
    '''
    Данная функция обрабатывает команду /delete и 
    удаляет пользователя из базы данных
    '''
    user_id = message.from_user.id
    await bot_run.send_message(user_id, 'Вы точно хотите удалить профиль?', reply_markup=markups.yes_no)
    await state.finish()
    await Form.ask_if_delete.set()
    
    
@dp.message_handler(state=Form.ask_if_delete)
async def answer_id_delete(message: types.Message, state):
    user_id = message.from_user.id
    if message.text == 'Да' or message.text == 'да':
        db.delete_user(user_id)
        await bot_run.send_message(user_id, 'Ваш профиль успешно удален.\nЧтобы снова зарегестрироваться, используйте команду /start .', reply_markup=ReplyKeyboardRemove())
        await state.finish()
    elif message.text == 'Нет' or message.text == 'нет':
        await bot_run.send_message(user_id, 'Мы очень рады, что вы остались.\nВозвращаем вас в главное меню', reply_markup=markups.main_menu)
        await state.finish()
        await Form.main_menu.set()
    else:
        await bot_run.send_message(user_id, 'Непонятный запрос, повторите попытку (Да или нет).')
        
        
@dp.message_handler(state=Form.main_menu, commands=['analyzer'])
async def analyzer(message: types.Message, state):
    await bot_run.send_message(message.from_user.id,
                               analyzer_message_tickers,
                               parse_mode='html',
                               reply_markup=markups.analyzer_tickers)
    await Form.analyzer_tickers.set()
    
    
@dp.message_handler(state=Form.analyzer_tickers)
async def analyzer_tickers(message: types.Message, state: FSMContext):
    text = message.text
    if text == 'В главное меню':
        await bot_run.send_message(message.from_user.id, 'Возврат в главное меню.', reply_markup=markups.main_menu)
        await state.finish()
        await Form.main_menu.set()
        return
    elif text == 'Использовать shares':
        shares = db.get_share(message.from_user.id)
        if not shares:
            await bot_run.send_message(message.from_user.id,
                                       'У вас нет shares. Уставновить shares можно с помощью команды /set_shares.\nВведите акции для анализа через пробел.',
                                       reply_markup=markups.to_main_menu)
            return
        else:
            async with state.proxy() as data:
                data['analyzer_tickers'] = shares
            await Form.analyzer_date.set()
            await bot_run.send_message(message.from_user.id,
                                       analyzer_message_date,
                                       reply_markup=markups.to_main_menu,
                                       parse_mode='html')
            return
    else:
        arr = text.split()
        async with state.proxy() as data:
            data['analyzer_tickers'] = arr
        await Form.analyzer_date.set()
        await bot_run.send_message(message.from_user.id,
                                    analyzer_message_date,
                                    reply_markup=markups.to_main_menu,
                                    parse_mode='html')
            
            
@dp.message_handler(state=Form.analyzer_date)
async def analyzer_date(message: types.Message, state: FSMContext):
    text = message.text
    if text == 'В главное меню':
        await bot_run.send_message(message.from_user.id, 'Возврат в главное меню.',
                                   reply_markup=markups.main_menu)
        await state.finish()
        await Form.main_menu.set()
        return
    else:
        dates = text.split()
        if len(dates) != 2:
            await bot_run.send_message(message.from_user.id,
                                       'Неправильный формат дат. Введите две даты в формате <b>yyyy-mm-dd</b> через пробел',
                                       parse_mode='html')
        else:
            try:
                datetime.datetime.strptime(dates[0], '%Y-%m-%d')
                datetime.datetime.strptime(dates[1], '%Y-%m-%d')
            except:
                await bot_run.send_message(message.from_user.id,
                                       'Неправильный формат дат. Введите две даты в формате <b>yyyy-mm-dd</b> через пробел',
                                       parse_mode='html')
                return
            if parse(dates[0]) > parse(dates[1]):
                await bot_run.send_message(message.from_user.id,
                                       'Дата окончания не может быть раньше даты начала.\nВведите две даты в формате <b>yyyy-mm-dd</b> через пробел',
                                       parse_mode='html')
                return
            async with state.proxy() as data:
                tickers = data['analyzer_tickers']
            try:
                analyzer = Analyzer(tickers, dates[0], dates[1], message.from_user.id)
                analyzer.sharpe_ratio()
                result = analyzer.text_analyser()
            except Exception as e:
                await bot_run.send_message(message.from_user.id,
                                       f"Произошла ошибка: {str(e)}\nВозврат в главное меню.",
                                       parse_mode='html',
                                       reply_markup=markups.main_menu)
                await state.finish()
                await Form.main_menu.set()
                return
            if result[1] is not None:
                await bot_run.send_message(message.from_user.id,
                                           result[1],
                                           parse_mode='html')
            await bot_run.send_message(message.from_user.id,
                                       result[0],
                                       parse_mode='html')
            await bot_run.send_message(message.from_user.id,
                                       "Возврат в главное меню.",
                                       reply_markup=markups.main_menu)
            await state.finish()
            await Form.main_menu.set()
            
            
        
@dp.message_handler(state=Form.main_menu)
async def main_menu_messages(message: types.Message, state):
    text = message.text
    if text == "Функции":
        await bot_run.send_message(message.from_user.id, help_message, parse_mode='html')
    elif text == "Профиль":
        await bot_run.send_message(message.from_user.id, profile_info(message.from_user.id), parse_mode='html')
    else:
        msg = await bot_run.send_message(message.from_user.id,
                                   'Сбой')
        await beautiful_messages(message.from_user.id,
                                 "Я такое не понимаю ...\nЧтобы узнать доступные команды, введите /help", msg)
        
        
@dp.message_handler()
async def smth(message: types.Message):
    '''
    Данная функция обрабатывает сообщения пользователя,
    на которые бот не сможет ответить
    '''
    msg = await bot_run.send_message(message.from_user.id, 'В')
    await beautiful_messages(message.from_user.id,
                                'Вы не зарегестрированы.\nИспользуйте команду /start, чтобы начать регистрацию.', msg)
        
    
async def beautiful_messages(user_id, message, msg, speed=0.8):
    for word in omg_hacked_text(message, speed=speed):
        await bot_run.edit_message_text(word, user_id, msg.message_id)
        
        
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