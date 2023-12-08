import pandas as pd
from tinkoff.invest import Client, RequestError, PortfolioResponse, PositionsResponse, GetAccountsResponse

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







