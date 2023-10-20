# # TOKEN = 't.wtbTq-3mtVbV_7R8Ma-HR6oObR4kIHCRCaQunedAxn5pIvoJ-uhHED1YFA8SKvQFvGNZdbtOCoiikNV38LiFeA'
# # account_id = '2176893218'
from tinkoff.invest import Client, RequestError, PortfolioResponse, PositionsResponse, PortfolioPosition
k =False

try:
    from tinkoff_test import TOKEN, account_id
except ImportError as i:
    k = True

import pandas as pd

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

# TOKEN = 't.aR38YYpBrtrkJezowoByFlvhDiOUl8ixFl9QLbnYPr-6x9pfuAL0IOpwjmPdBFI-sNt25Ln1BT9SlhoH1V2WoA'
# account_id = '2164016111'
def run():

    try:
        with Client(TOKEN) as client:
            u = client.market_data.get_last_prices(figi=['USD000UTSTOM'])
            usdrur = cast_money(u.last_prices[0].price)

            r : PortfolioResponse = client.operations.get_portfolio(account_id=account_id)
            df = pd.DataFrame([portfolio_pose_todict(p, usdrur) for p in r.positions])
            print(df.head(100))

            print("bonds", cast_money(r.total_amount_bonds), df.query("instrument_type == 'bond'")['sell_sum'].sum(), sep=" : ")
            print("etfs", cast_money(r.total_amount_etf), df.query("instrument_type == 'etf'")['sell_sum'].sum(), sep=" : ")
            print("shares", cast_money(r.total_amount_shares), df.query("instrument_type == 'share'")['sell_sum'].sum(), sep=" : ")
            print(df['comission'].sum())

    except RequestError as e:
        print(str(e))

def portfolio_pose_todict(p : PortfolioPosition, usdrur):
    r = {
        'figi': p.figi,
        'quantity': cast_money(p.quantity),
        'expected_yield': cast_money(p.expected_yield),
        'instrument_type': p.instrument_type,
        'average_buy_price': cast_money(p.average_position_price),
        'currency': p.average_position_price.currency
    }

    if r['currency'] == 'usd':
        r['expected_yield'] *= usdrur
        r['average_buy_price'] *= usdrur

    r['sell_sum'] = (r['average_buy_price']*r['quantity']) + r['expected_yield']
    r['comission'] = r['sell_sum']*0.003
    r['comission'] += r['expected_yield']*0.013 if r['expected_yield'] > 0 else 0

    return r

def cast_money(v):
    return v.units + v.nano / 1e9  # nano - 9 нулей

if k == True:
    pass
else:
    run()