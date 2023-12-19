import requests
import apimoex
import pandas as pd


TIMEFRAMES = ['M1', 'M10', 'H1', 'D1', 'W1', 'MN1']
dict_timeframes = {
    'M1': 1,
    'M5': 10,
    'M10': 10,
    'H1': 60,
    'D1': 24,
    'W1': 7,
    'MN1': 31,
}
def get_symbol_names():
    request_url = ('https://iss.moex.com/iss/engines/stock/'
                   'markets/shares/boards/TQBR/securities.json')
    with requests.Session() as session:
        iss = apimoex.ISSClient(session, request_url)
        data = iss.get()
        df = pd.DataFrame(data['securities'])
        return pd.DataFrame(df["SECID"])["SECID"].tolist()


