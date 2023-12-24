from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
from pandas import DataFrame
from tinkoff_test import TOKEN, account_id
from tinkoff.invest import Client, RequestError, PositionsResponse, AccessLevel, OperationsResponse, Operation, \
    OperationState, OperationType
from tinkoff.invest.services import Services


pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


def run():
    try:
        with Client(TOKEN) as client:
            Position(client).print()
    except RequestError as e:
        print(e)

class Position:
    def __init__(self, client : Services): # def __init__(self, client : Services, доп параметр - валюта, как конструктор по умолчанию):
        self.usdrur = None
        self.client = client
        self.accounts = []

    def print(self): #вывод нужной информации
        df = self.get_operations_df(account_id)
        # df = df[df['otype'] == OperationType.OPERATION_TYPE_TAX]
        # df = df[df['otype'].isin([
        #     OperationType.OPERATION_TYPE_BOND_TAX
        #
        # ])]
        # df = df[df['otype'] == OperationType.OPERATION_TYPE_BROKER_FEE]

        print(df)
        # print(df['payment'].sum())

    def get_usdrur(self): #получаем курс нужной валюты по запросу
        if not self.usdrur:
            u = self.client.market_data.get_last_prices(figi=['USD000UTSTOM'])
            self.usdrur = self.cast_money(u.last_prices[0].price)

        return self.usdrur

    def get_operations_df(self, account_id: str) -> Optional[DataFrame]:
        # Преобразование класса PortfolioResponce в pandas.DataFrame
        r: OperationsResponse = self.client.operations.get_operations(
            account_id=account_id,
            from_=datetime(2015,1,1),
            to = datetime.utcnow()
        )

        if len(r.operations) <1: return None
        df = pd.DataFrame([self.operation_todict(p, account_id) for p in r.operations])
        return df


    def operation_todict(self, o: Operation, account_id: str):
        r = {
            'acc': account_id,
            'date': o.date,
            'type': o.type,
            'otype': o.operation_type,
            'currency': o.currency,
            'instrument_type': o.instrument_type,
            'figi': o.figi,
            'quantiy': o.quantity,
            'state': o.state,
            'payment': self.cast_money(o.payment, True),#здесь тру надо передавать как входной параметр
            'price': self.cast_money(o.price, True)#здесь тру надо передавать как входной параметр
        }
        return r




    def cast_money(self, v, to_rub = True):
        r = v.units + v.nano / 1e9
        if to_rub and hasattr(v, 'currency') and getattr(v, 'currency') == 'usd':
            r *= self.get_usdrur()
        return r



run()
