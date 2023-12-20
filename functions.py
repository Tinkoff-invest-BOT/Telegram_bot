import yfinance as yf
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from io import BytesIO
import chardet
from tinkoff.invest import Client, RequestError, PortfolioResponse, PositionsResponse, GetAccountsResponse
import pandas as pd
from db import *



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
    res = result.split(",")
    account_id = res[0]
    access_level = res[1]
    return account_id, access_level


