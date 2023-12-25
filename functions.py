import datetime

import yfinance as yf
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from io import BytesIO
import chardet
from tinkoff.invest import Client, RequestError, PortfolioResponse, PositionsResponse, GetAccountsResponse, \
    OrderDirection, OrderType, Quotation, PortfolioPosition
import pandas as pd
from db import *
from random import random, randint
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import base64
from parser_daily import parse_moex, parse_yahoo
db = Database(connection)



db = Database(connection)

def language_check(smth):
    try:
        if chardet.detect(smth.encode('cp1251'))['language'] == 'Russian':
            result = 1
            return result
    except UnicodeEncodeError as e:
        result = 2
        return result
    return 3

def get_id(r: GetAccountsResponse):
    df = ([{
        c.id: [c.name, c.access_level]
    } for c in r.accounts])
    return df

def beauty_df(r):
    df = pd.DataFrame([{
        'name' : c.name
    } for c in r.accounts])
    return df

def get_account_id(r, a):
    mp = get_id(r)
    broc_accs = []
    for i in mp:
        tmp = list(i.values())[0][0].lower()
        if str(tmp).replace('ё', 'е') == a.lower().replace('ё', 'е'):

            broc_accs.append({int(list(i.keys())[0]): list(i.values())[0][1]})
    return broc_accs



def show_accounts(TOKEN):
    with Client(TOKEN) as client:
        r = client.users.get_accounts()
        return beauty_df(r)

def choose_account(TOKEN, string):
    with Client(TOKEN) as client:
        r = client.users.get_accounts()
        df = beauty_df(r)
        result  = get_id(r)
        account_id = get_account_id(r, string)
        return (account_id)

def token_check(TOKEN):
    try:
        if chardet.detect(TOKEN.encode('cp1251'))['language'] == 'Russian':
            result = 2
            return result
    except UnicodeEncodeError as e:
        result = 3
        return result
    else:
        try:
            with Client(TOKEN) as client:
                try:
                    r = client.users.get_accounts()
                    result = 0
                except RequestError as e:
                    result = 1
        except ValueError as e:
            result = 1
        return result

def share_check(share):
    result = db.share_exist(share)
    if result:
        return True
    return False

def create_pdf_from_dataframe(dataframe):
    output = BytesIO()
    doc = SimpleDocTemplate(output, pagesize=letter)
    elements = []
    doc.encoding = "utf-8"
    table_data = [list(dataframe.columns)] + dataframe.values.tolist()
    table = Table(table_data)
    table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), (0.8, 0.8, 0.8))]))
    elements.append(table)
    doc.build(elements)
    return output


def check_share_moex(share:str):
    ticker = share
    from_ = '2022-12-15'
    till = '2022-12-16'
    interval = 24
    query = f'http://iss.moex.com/iss/engines/stock/markets/shares/securities/{ticker}/candles.csv?from={from_}&till={till}&interval={interval}'
    df = pd.read_csv(query, sep=';', header=1)
    df['ticker'] = ticker
    df['month'] = pd.to_datetime(df['end']).dt.strftime('%Y-%m-01')
    df.set_index('end', inplace=True)
    if len(df) == 0:
        return False
    return True

def check_share_yahoo(share):
    try:
        data = yf.download(share, start= "2023-10-01", end = "2023-10-03", interval = "1d")
    except:
        data = []
    if (len(data)) == 0:
        return False
    return True

def add_shares(shares_list: list):
    shares_dict = {}
    counter = 0
    for i in shares_list:
        result = db.get_ticker_parser(i)
        if result == False:
            if not check_share_moex(i):
                if not check_share_yahoo(i):
                    counter = 1
                    shares_list.remove(i)
                else:
                    shares_dict[i] = "yahoo"
                    db.set_share_to_parser(i)
                    db.set_parser_to_share(i, "yahoo")
            else:
                shares_dict[i] = "moex"
                db.set_share_to_parser(i)
                db.set_parser_to_share(i, "moex")
        else:
            pass

    shares_list = list(set(shares_list))
    return shares_list, counter

def token_access_level(user_id):
    result = db.get_token_status(user_id)
    if result[0] != "without_token":
        res = result[0].split(",")
        account_id = res[0]
        access_level = res[1]
        return account_id, access_level
    return False


def buy_share_market(TOKEN, figi, price, quantity, account_id):
    flag = 0
    flag2 = 0
    try:
        if "." in price:
            tmp = price.split(".")[0]
            flag = 1
        else:
            tmp = int(price)
            flag = 2
    except:
        flag = 0

    if flag == 1:
        price2 = Quotation(units=int(price.split(".")[0]), nano=int(price.split(".")[1]))
    elif flag == 2:
        price2 = Quotation(units=int(price), nano=0)
    else:
        flag2 = 1
        price2 = ''

    if flag2 == 0:
        with Client(TOKEN) as c:
            r = c.orders.post_order(
                order_id=str(datetime.datetime.utcnow().timestamp()),
                figi=figi,
                price=price2,
                quantity=quantity,
                account_id=account_id,
                direction=OrderDirection.ORDER_DIRECTION_SELL,
                order_type=OrderType.ORDER_TYPE_MARKET
            )
    else:
        with Client(TOKEN) as c:
            r = c.orders.post_order(
                order_id=str(datetime.datetime.utcnow().timestamp()),
                figi=figi,
                quantity=quantity,
                account_id=account_id,
                direction=OrderDirection.ORDER_DIRECTION_BUY,
                order_type=OrderType.ORDER_TYPE_MARKET
            )
    return r


def sell_share_market(TOKEN, figi, price, quantity, account_id):
    flag = 0
    flag2 = 0
    try:
        if "." in price:
            tmp = price.split(".")[0]
            flag = 1
        else:
            tmp = int(price)
            flag = 2
    except:
        flag = 0

    if flag == 1:
        price2 = Quotation(units=int(price.split(".")[0]), nano=int(price.split(".")[1]))
    elif flag == 2:
        price2 = Quotation(units=int(price), nano=0)
    else:
        flag2 = 1
        price2 = ''

    if flag2 == 0:
        with Client(TOKEN) as c:
            r = c.orders.post_order(
                order_id=str(datetime.datetime.utcnow().timestamp()),
                figi=figi,
                price=price2,
                quantity=quantity,
                account_id=account_id,
                direction=OrderDirection.ORDER_DIRECTION_SELL,
                order_type=OrderType.ORDER_TYPE_MARKET
            )
    else:
        with Client(TOKEN) as c:
            r = c.orders.post_order(
                order_id=str(datetime.datetime.utcnow().timestamp()),
                figi=figi,
                quantity=quantity,
                account_id=account_id,
                direction=OrderDirection.ORDER_DIRECTION_SELL,
                order_type=OrderType.ORDER_TYPE_MARKET
            )
    return r

def buy_share_limit(TOKEN, figi, price, quantity, account_id):
    flag = 0
    try:
        if "." in price:
            tmp = price.split(".")[0]
            flag = 1
        else:
            tmp = int(price)
            flag = 2
    except:
        flag = 0
        return "ERROR"

    if flag == 1:
        price2 = Quotation(units=int(price.split(".")[0]), nano=int(price.split(".")[1]))
    elif flag == 2:
        price2 = Quotation(units=int(price), nano=0)
    else:
        return "такой ошибки не может быть, вы сломали Питон"

    with Client(TOKEN) as c:
        r = c.orders.post_order(
            order_id=str(datetime.datetime.utcnow().timestamp()),
            figi=figi,
            price=price2,
            quantity=quantity,
            account_id=account_id,
            direction=OrderDirection.ORDER_DIRECTION_BUY,
            order_type=OrderType.ORDER_TYPE_LIMIT
        )
    return r

def sell_share_limit(TOKEN, figi, price, quantity, account_id):
    flag = 0
    try:
        if "." in price:
            tmp = price.split(".")[0]
            flag = 1
        else:
            tmp = int(price)
            flag = 2
    except:
        flag = 0
        return "ERROR"

    if flag == 1:
        price2 = Quotation(units=int(price.split(".")[0]), nano=int(price.split(".")[1]))
    elif flag == 2:
        price2 = Quotation(units=int(price), nano=0)
    else:
        return "такой ошибки не может быть, вы сломали Питон"
    with Client(TOKEN) as c:
        r = c.orders.post_order(
            order_id=str(datetime.datetime.utcnow().timestamp()),
            figi=figi,
            price=price2,
            quantity=quantity,
            account_id=account_id,
            direction=OrderDirection.ORDER_DIRECTION_SELL,
            order_type=OrderType.ORDER_TYPE_LIMIT
        )
    return r


def before_buying_market(user_id, tiker, lots, price="best_price"):
    TOKEN = db.get_token(user_id)
    if TOKEN is None:
        return '0'
    query = token_access_level(user_id)
    if not query:
        return '0'
    account_id = query[0]
    access_level = query[1]

    if int(access_level) != 1:
        return '2'

    print('b_m', TOKEN, account_id, access_level)
    if not share_check(tiker):
        return '3'
    figi = db.ticker_to_figi(tiker)

    try:
        q = buy_share_market(TOKEN, figi, price, lots, account_id)
        return q
    except Exception as e:
        try:
            error_code = str(e).split(',')[2].strip()[1:-1]
            return error_code
        except:
            return '-1'

def before_selling_market(user_id, tiker, lots, price="best_price"):
    TOKEN = db.get_token(user_id)
    if TOKEN is None:
        return '0'
    query = token_access_level(user_id)
    if not query:
        return '0'
    account_id = query[0]
    access_level = query[1]

    if int(access_level) != 1:
        return '2'

    print('s_m', TOKEN, account_id, access_level)
    if not share_check(tiker):
        return '3'
    figi = db.ticker_to_figi(tiker)

    try:
        q = sell_share_market(TOKEN, figi, price, lots, account_id)
        return q
    except Exception as e:
        try:
            error_code = str(e).split(',')[2].strip()[1:-1]
            return error_code
        except:
            return '-1'


def before_buying_limit(user_id, tiker, lots, price):
    TOKEN = db.get_token(user_id)
    if TOKEN is None:
        return '0'
    query = token_access_level(user_id)
    if not query:
        return '0'
    account_id = query[0]
    access_level = query[1]

    if int(access_level) != 1:
        return '2'

    print('s_l', TOKEN, account_id, access_level)
    if not share_check(tiker):
        return '3'
    figi = db.ticker_to_figi(tiker)
    try:
        q = buy_share_limit(TOKEN, figi, price, lots, account_id)
        return q
    except Exception as e:
        try:
            error_code = str(e).split(',')[2].strip()[1:-1]
            return error_code
        except:
            return '-1'


def before_selling_limit(user_id, tiker, lots, price):
    TOKEN = db.get_token(user_id)
    if TOKEN is None:
        return '0'
    query = token_access_level(user_id)
    if not query:
        return '0'
    account_id = query[0]
    access_level = query[1]

    if int(access_level) != 1:
        return '2'

    print('s_l', TOKEN, account_id, access_level)
    if not share_check(tiker):
        return '3'
    figi = db.ticker_to_figi(tiker)
    try:
        q = buy_share_limit(TOKEN, figi, price, lots, account_id)
        return q
    except Exception as e:
        try:
            error_code = str(e).split(',')[2].strip()[1:-1]
            return error_code
        except:
            return '-1'
        

def profile_info(user_id):
    text = f'<b>id</b>: {user_id}\n'
    text += f"<b>nickname</b>: {db.get_nickname(user_id)}\n"
    text += f"<b>email</b>: {db.get_email(user_id)}\n"
    if db.get_token_status(user_id) == 'without_token':
        text += "<b>has_token</b>: no\n"
    else:
        text += "<b>has_token</b>: yes\n"
    shares = db.get_share(user_id)
    if shares:
        text += "<b>shares</b>:"
        for i in shares:
            text += f" {i},"
        text = text[:-1] + '\n'
    else:
        text += "<b>shares</b>: None\n"
    levels = db.get_levels(user_id)
    if levels:
        text += f"<b>levels</b>: {levels}"
    else:
        text += f"<b>levels</b>: None"
    return text
    


# a = before_buying(1297355532, "TMOS", 1 )
# print(a)
# a = before_selling(1297355532, "TMOS",  1, 6.16)
# print(a)
# a = before_buying(1297355532, "TMOS", "best", 1)
# print(a)
# a = before_selling(1297355532, "TMOS", "best", 1)
# print(a)
# a = before_buying(1297355532, "TMOS", "best", 1)
# print(a)

# buy_share(1297355532)
# buy_share(446927518)
# def f(TOKEN):
#     with Client(TOKEN) as c:
#         res = c.users.get_info()
#         print(res)

# f("t.aR38YYpBrtrkJezowoByFlvhDiOUl8ixFl9QLbnYPr-6x9pfuAL0IOpwjmPdBFI-sNt25Ln1BT9SlhoH1V2WoA")


def cast_money(v):
    return v.units + v.nano / 1e9


def portfolio_pose_todict(p: PortfolioPosition):
    r = {
        'figi': p.figi,
        'quantity': cast_money(p.quantity),
        'expected_yield': cast_money(p.expected_yield),
        'instrument_type': p.instrument_type,
        'average_buy_price': cast_money(p.average_position_price),
        'currency': p.average_position_price.currency
    }

    r['sell_sum'] = (r['average_buy_price'] * r['quantity']) + r['expected_yield']
    r['comission'] = r['sell_sum'] * 0.003
    r['comission'] += r['expected_yield'] * 0.013 if r['expected_yield'] > 0 else 0

    return r


def get_portfolio_(user_id):
    TOKEN = db.get_token(user_id)
    query = token_access_level(user_id)
    if not query:
        return '0'
    account_id = query[0]
    try:
        with Client(TOKEN) as client:
            r: PortfolioResponse = client.operations.get_portfolio(account_id=account_id)
            df = pd.DataFrame([portfolio_pose_todict(p) for p in r.positions])
            return df
    except Exception as e:
        try:
            error_code = str(e).split(',')[2].strip()[1:-1]
            return error_code
        except:
            return '-1'



def photo_generating(ticker):
    from_where = db.get_ticker_parser(ticker=ticker)
    if from_where[0] == 'moex':
        df = parse_moex(ticker=ticker, flag='graph')[::-1]
        plt.figure(figsize=(14, 7))
        plt.plot(df['begin'], df['close'], markersize=4, label='Цена закрытия в руб.')

        ticks = plt.gca().get_xticks()
        plt.gca().set_xticks(ticks[::15])
        plt.gcf().autofmt_xdate() 

        plt.title(f'График цены закрытия {ticker}')
        plt.xlabel('Дата')
        plt.ylabel('Цена закрытия')
        plt.legend()

        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        buffer.close()
        plt.close()
        return image_base64
    
    elif from_where[0] == 'yahoo':
        df = parse_yahoo(ticker=ticker, flag='graph').reset_index()

        plt.figure(figsize=(14, 7))
        plt.plot(df['Datetime'], df['Close'], markersize=4, label='Цена закрытия в $')

        ax = plt.gca()
        ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=7, maxticks=7))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        
        plt.gcf().autofmt_xdate() 
        plt.title(f'График цены закрытия {ticker}')
        plt.xlabel('Дата')
        plt.ylabel('Цена закрытия')
        plt.legend()

        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        buffer.close()
        plt.close()
        return image_base64

def get_glass(figi, TOKEN):
    with Client(TOKEN) as client:
        book = client.market_data.get_order_book(figi=figi, depth=50)
        bids = [cast_money(p.price) for p in book.bids]
        asks = [cast_money(p.price) for p in book.asks]
        if len(bids) == 0 and len(asks) == 0:
            return 30079
        length_a = min(len(asks), 5)
        tmp_a = '\n'.join(f'\t{asks[i]}' for i in range(length_a))

        length_b = min(len(bids), 5)
        tmp_b = '\n'.join(f'\t{bids[i]}' for i in range(length_b))

        string = f'''
        -------------
        АСКИ
        {tmp_a}
        ---       --- 
        {tmp_b}
        БИДЫ
        -------------
        '''
        return string

