from datetime import timedelta, timezone 
from db import Database 
from pandas import DataFrame 
from connection_db import connection 
from tinkoff.invest import Client, CandleInterval, RequestError 
from passwords import * 
import pandas as pd
import datetime
import yfinance as yf


db = Database(connection) 


def notify_user_about_stocks(user_id): 
    ''' 
    Функция формирует сообщении о стоимости акций для каждого пользователя 
    ''' 
    message = '' 
    shares_list = db.get_share(user_id)  
    if shares_list: 
        stocks_info = stock_price_change(shares_list, user_id, CandleInterval.CANDLE_INTERVAL_HOUR, 0) 
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
 
 
def stock_price_change(shares_figi, user_id, interval : CandleInterval, delta): 
    ''' 
    С помощью "свечей" Тинькоффа находим в этой функции цену закрытия предыдущего дня и нынешнюю цену. 
    Затем считаем процентную разницу 
    ''' 
    pct_changes = dict() 
    if db.get_token(user_id=user_id) != None: 
        TOKEN = db.get_token(user_id=user_id) 
    else: 
        TOKEN = TOKEN_SH 
     
    for figi in shares_figi:      
        figi_use = db.ticker_to_figi(figi) 
 
        with Client(TOKEN) as client: 
            r = client.market_data.get_candles( 
                figi=figi_use, 
                from_=datetime.now() - timedelta(days = 1), 
                to=datetime.now(), 
                interval=interval 
            ) 
             
            df = create_df(r.candles) 
            if not delta:
                delta = len(df)
            if not df.empty: 
                previous_close_price = df['close'][len(df) - delta] 
                current_price =  df['close'][len(df) - 1] 
                pct_change = ((current_price - previous_close_price) / previous_close_price) * 100 
            else: 
                previous_close_price = 0 
                current_price = 0 
                pct_change = 0 
 
            pct_changes[figi] = pct_change              
    return pct_changes 
 
 
def pct_checker(user_id): 
    ''' 
    Функция формирует сообщение для пользователя об измненении стоимости акции (если abs() >= 5) 
    ''' 
    shares_list = db.get_share(user_id) 
    message = '' 
    if shares_list: 
        stocks_info = stock_price_change(shares_list, user_id, CandleInterval.CANDLE_INTERVAL_HOUR, 15) 
        for comp in stocks_info.keys(): 
            if abs(stocks_info[comp]) >= 5: 
                if stocks_info[comp] >= 5: 
                    message += f'{comp} в портфеле вырос на {round(stocks_info[comp], 3)}% 🚀\n' 
                elif stocks_info[comp] <= 5: 
                    message += f'{comp} в портфеле упал на {round(stocks_info[comp], 3)}% 🗿\n' 
                     
    if message: 
        message = '<b>AHTUNG!</b> Стоимости акций меняются!\n' + message + '<b>Проверьте прямо сейчас!</b>' 
    return message
        

def parse_moex(ticker, flag):
    if flag == 'graph':
        timeframe = '1hour'
        delta = datetime.timedelta(days=7)
    elif flag == 'checker':
        timeframe = '1min' 
        delta = datetime.timedelta(minutes=2)
    from_ = (datetime.datetime.now() - delta).strftime("%Y-%m-%d")
    till = datetime.datetime.now().strftime("%Y-%m-%d")
    query = f'http://iss.moex.com/iss/engines/stock/markets/shares/securities/{ticker}/candles.csv?iss.meta=on&iss.reverse=true&from={from_}&till={till}&interval={timeframe}'
    df = pd.read_csv(query, sep=';', header=1)
    df['end'] = pd.to_datetime(df['end'])

    if not df.empty:
        if flag == 'graph':
            return df
        else:
            return list(df['close'].iloc[0 : 60])
    else:
        return None

       
def parse_yahoo(ticker, flag):
    if flag == 'graph':
        timeframe = '1h'
        delta = datetime.timedelta(days=7)
    elif flag == 'checker':
        timeframe = '1m'
        delta = datetime.timedelta(hours=2)

    now = datetime.datetime.now()
    start_date = now - delta
    try:
        data = yf.download(ticker, start=start_date.strftime("%Y-%m-%d"), interval=timeframe)
        if flag == 'graph':
           return data
        elif flag == 'checker':
            return list(data['Close'].tail(60))
    except:
        return None


def price_checker(user_id):
    info = db.get_levels(user_id=user_id)
    message = ''
    for key in info.keys():
        flag = 0
        platform = db.get_ticker_parser(key)[0]
        if platform == 'moex':
            prices = parse_moex(key, 'checker')
        elif platform == 'yahoo':
            prices = parse_yahoo(key, 'checker')
        if prices is None:
            print("Выходной!")
            flag = 1
        if flag == 0:
            for sign in info[key].keys():
                if sign == '+':
                    final = next((price for price in prices if info[key]['+'] <= price), None)
                    if final:
                        db.delete_level(user_id=user_id, ticker=key)
                        message += f"Стоимость {key} превысила {info[key]['+']}. Сейчас: {final}.\n<b>Бегом проверять!</b>\nТеперь {key} не отслеживается."

                elif sign == '-':
                    final = next((price for price in prices if info[key]['-'] >= price), None)
                    if final:
                        db.delete_level(user_id=user_id, ticker=key)
                        message += f"Стоимость {key} упала ниже {info[key]['-']}. Сейчас: {final}.\n<b>Бегом проверять!</b>\nТеперь {key} не отслеживается."
    if message != '':
        return message
    return False



# db.set_levels(user_id=446927518, data=['TSLA', '-', 253])
# print(db.get_ticker_parser(ticker='TSLA'))
