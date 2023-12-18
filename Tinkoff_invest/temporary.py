from tinkoff.invest import Client, RequestError, PortfolioResponse, PositionsResponse, PortfolioPosition
import pandas as pd
# from bot import db
from new_bot import db
TOKEN = 't.aR38YYpBrtrkJezowoByFlvhDiOUl8ixFl9QLbnYPr-6x9pfuAL0IOpwjmPdBFI-sNt25Ln1BT9SlhoH1V2WoA'
account_id = '2164016111'

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

# def f():
#     from bot import db


def portfolio_pose_todict(p : PortfolioPosition, usdrur):
    if p.figi[0:4] != 'BBG0':
        r = {
            'figi': p.figi,
            'quantity': cast_money(p.quantity),
            'expected_yield': cast_money(p.expected_yield),
            'instrument_type': p.instrument_type,
            'average_buy_price': cast_money(p.average_position_price),
        }
    else:
        r = {
            'figi': db.get_figi(p.figi),
            'quantity': cast_money(p.quantity),
            'expected_yield': cast_money(p.expected_yield),
            'instrument_type': p.instrument_type,
            'average_buy_price': cast_money(p.average_position_price),
        }

    if p.average_position_price.currency == 'usd':
        r['expected_yield'] *= usdrur
        r['average_buy_price'] *= usdrur

    r['sell_sum'] = (r['average_buy_price']*r['quantity']) + r['expected_yield']
    r['sell_sum'] = round(r['sell_sum'], 2)
    r['comission'] = r['sell_sum']*0.003
    r['comission'] += r['expected_yield']*0.013 if r['expected_yield'] > 0 else 0
    r['comission'] = round(r['comission'], 2)

    return r

def cast_money(v):
    return v.units + v.nano / 1e9

with Client(TOKEN) as client:
    u = client.market_data.get_last_prices(figi=['USD000UTSTOM'])
    usdrur = cast_money(u.last_prices[0].price)

    r : PortfolioResponse = client.operations.get_portfolio(account_id=account_id)
    df = pd.DataFrame([portfolio_pose_todict(p, usdrur) for p in r.positions])
    df_html = df.to_html()
    df_str = df.to_string()
    dww = df.to_numpy()