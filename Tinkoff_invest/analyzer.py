import pandas as pd
import numpy as np
from pandas_datareader import data as pdr
import yfinance as yfin
from connection_db import connection
from db import Database
import datetime
from tinkoff.invest import Client, CandleInterval
from parser_daily import cast_money

db = Database(connection)

class Analyzer:
    def __init__(self, stocks_names: list, start_date : str, end_date : str, user_id: int):
        self.stocks_names = stocks_names
        self.start_date = start_date
        self.end_date = end_date
        self.user_id = user_id
        self.data = pd.DataFrame()
        self.analysis = pd.DataFrame()
        
    def yahoo_stocks_parse(self, stocks_names : list):
        # get not russian stocks
        # returns pd.DF: cols - [date, stocks_names...], rows - [date, stocks_price...]
        yfin.pdr_override()
        data = pdr.get_data_yahoo(stocks_names, start=self.start_date, end=self.end_date)['Adj Close']
        if len(stocks_names) == 1:
            data = data.rename(stocks_names[0])
        data = data.reset_index()
        data['Date'] = data['Date'].apply(lambda x: x.date())
        data = data.set_index('Date')
        if self.data.size == 0:
            self.data = data.fillna(method='bfill').fillna(method='ffill')
        else:
            self.data = self.data.join(data)
            self.data = self.data.fillna(method='bfill').fillna(method='ffill')
            
    def tinkoff_stocks_parse(self, stocks_names : list):
        TOKEN = db.get_token(user_id=self.user_id)
        if TOKEN == None:
            TOKEN = "t.wtbTq-3mtVbV_7R8Ma-HR6oObR4kIHCRCaQunedAxn5pIvoJ-uhHED1YFA8SKvQFvGNZdbtOCoiikNV38LiFeA"
        data = pd.DataFrame()
        
        for name in stocks_names:
            figi = db.ticker_to_figi(name)
            print(figi)
            with Client(TOKEN) as client:
                r = client.market_data.get_candles(
                    figi=figi,
                    from_=datetime.datetime.strptime(self.start_date, "%Y-%m-%d") + datetime.timedelta(days=1),
                    to=datetime.datetime.strptime(self.end_date, "%Y-%m-%d") + datetime.timedelta(days=1),
                    interval=CandleInterval.CANDLE_INTERVAL_DAY
                )
                
                df = pd.DataFrame([{
                    'time': c.time,
                    'close': cast_money(c.close)
                } for c in r.candles])
                
                data[name] = df['close']
                data['Date'] = df['time'].apply(lambda x: x.date())
        data = data.set_index('Date')
        if self.data.size == 0:
            self.data = data.fillna(method='bfill').fillna(method='ffill')
        else:
            self.data = self.data.join(data)
            self.data = self.data.fillna(method='bfill').fillna(method='ffill')
                
        
    
    def get_overall_col_in_data(self):
        self.data['Overall'] = self.data.apply(lambda x: sum(x[name] for name in self.stocks_names), axis=1)
        
    def sharpe_ratio(self, rfr: float):
        # returns DataFrame: cols - stocks, row - sharpe ratio
        std = self.data.apply(lambda x: x.pct_change().std() * np.sqrt(len(self.data)))
        cumulative = self.data.apply(lambda x: (x[len(self.data) - 1] / x[0]) - 1)
        sharpe = (cumulative - rfr) / std
        
        analysis = pd.DataFrame([std, cumulative, sharpe])
        analysis['index'] = ['std', 'cumulative', 'sharpe']
        if self.analysis.size == 0:
            self.analysis = analysis
            return
        
        indexes = np.setdiff1d(analysis['index'], self.analysis['index'])
        for i in indexes:
            self.analysis = pd.concat([self.analysis, analysis[analysis['index'] == i]])
        
anal = Analyzer(['AAPL', 'TSLA'], '2022-02-01', '2023-01-01', 1297355532)
anal.yahoo_stocks_parse(anal.stocks_names)
anal.yahoo_stocks_parse(["GOOG"])
anal.tinkoff_stocks_parse(["YNDX"])
anal.get_overall_col_in_data()
anal.sharpe_ratio(0.02)
print(anal.analysis)
        