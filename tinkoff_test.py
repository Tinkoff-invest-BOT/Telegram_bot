import Cython
import os
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

print("Введите токен от своего аккаунта")
TOKEN = input()
try:
    with Client(TOKEN) as client:
        r = client.users.get_accounts()
        print(beauty_df(r))
        print('Выбери конкретный аккаунт(введи название)')
        a = input()
        print("Загрузка...")
        try:
            account_id = str(list(get_account_id(r, a)[0].keys())[0])
            print("Успешно!")
                  # f"\n  Ваш account id -  {account_id}")

        except:
            print('Неверное название аккаунта')

except:
    print("Несуществующий токен")


