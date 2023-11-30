from tinkoff.invest import Client
from datetime import datetime, timedelta, timezone
from db import Database
from pandas import DataFrame
from connection_db import connection
from ta.trend import ema_indicator
from aiogram import Bot, Dispatcher
from aiogram.utils.executor import start_webhook
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from tinkoff.invest import Client, CandleInterval, RequestError



db = Database(connection)



def notify_user_about_stocks(user_id):
    '''
    Функция формирует сообщении о стоимости акций для каждого пользователя
    '''
    message = ''
    shares_list = db.get_share(user_id) 
    if shares_list:
        stocks_info = stock_price_change(shares_list, user_id)
        for comp in stocks_info.keys():
            message += f'• Акции {db.ticker_to_name(comp)[0]} изменились на: {round(stocks_info[comp], 3)}% \n'
    return message


def create_df(candles):
    df = DataFrame([{
        'time': c.time,
        'volume': c.volume,
        'open': cast_money(c.open),
        'close': cast_money(c.close),
        'high': cast_money(c.high),
        'low': cast_money(c.low),
    } for c in candles])

    return df


def cast_money(v):
    return v.units + v.nano / 1e9


def stock_price_change(shares_figi, user_id):
    '''
    С помощью "свечей" Тинькоффа находим в этой функции цену закрытия предыдущего дня и нынешнюю цену.
    Затем считаем процентную разницу
    '''
    pct_changes = dict()
    if db.get_token(user_id=user_id) != None:
        TOKEN = db.get_token(user_id=user_id)
    else:
        TOKEN = "t.wtbTq-3mtVbV_7R8Ma-HR6oObR4kIHCRCaQunedAxn5pIvoJ-uhHED1YFA8SKvQFvGNZdbtOCoiikNV38LiFeA"
    
    for figi in shares_figi:     
        figi_use = db.ticker_to_figi(figi)

        with Client(TOKEN) as client:
            r = client.market_data.get_candles(
                figi=figi_use,
                from_=datetime.now() - timedelta(days = 1),
                to=datetime.now(),
                interval=CandleInterval.CANDLE_INTERVAL_10_MIN
            )
            
            df = create_df(r.candles)
            
            if not df.empty:
                previous_close_price = df['close'][0]
                current_price =  df['close'][len(df) - 1]
                pct_change = ((current_price - previous_close_price) / previous_close_price) * 100
            else:
                previous_close_price = 0
                current_price = 0
                pct_change = 0

            pct_changes[figi] = pct_change             

    return pct_changes

