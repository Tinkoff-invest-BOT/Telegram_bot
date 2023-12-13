import pandas as pd
import numpy as np
from pandas_datareader import data as pdr
import yfinance as yfin
from connection_db import connection
from db import Database
import datetime
from tinkoff.invest import Client, CandleInterval
from parser_daily import cast_money
from passwords import *
db = Database(connection)

class Analyzer:
    def __init__(self, stocks_tickers: list, start_date : str, end_date : str, user_id: int):
        self.stocks_tickers = stocks_tickers
        self.start_date = start_date
        self.end_date = end_date
        self.user_id = user_id
        self.data = pd.DataFrame()
        self.analysis = pd.DataFrame()
        
        try:
            self.parse_all()
        except:
            raise ValueError("Неправильное название акции")
    
    def text_analyser(self):
        text = 'Результаты анализа:\n'
        for i in self.analysis[self.analysis.index == 'sharpe'].columns():
            text += i + ' - ' + self.analysis[self.analysis.index == 'sharpe'][i] + '\n'
        return text
            
    
    def parse_all(self):
        yahoo_tickers = np.setdiff1d(self.stocks_tickers, db.get_all_tinkoff_tickers())
        tinkoff_tickers = np.setdiff1d(self.stocks_tickers, yahoo_tickers)
        
        self.__yahoo_stocks_parse(yahoo_tickers)
        self.__tinkoff_stocks_parse(tinkoff_tickers)
        self.__get_overall_col_in_data()
        
    def __yahoo_stocks_parse(self, stocks_tickers : list):
        # get not russian stocks
        # returns pd.DF: cols - [date, stocks_names...], rows - [date, stocks_price...]
        yfin.pdr_override()
        data = pdr.get_data_yahoo(stocks_tickers, start=self.start_date, end=self.end_date)['Adj Close']
        if len(stocks_tickers) == 1:
            data = data.rename(stocks_tickers[0])
        data = data.reset_index()
        data['Date'] = data['Date'].apply(lambda x: x.date())
        data = data.set_index('Date')
        if self.data.size == 0:
            self.data = data.fillna(method='bfill').fillna(method='ffill')
        else:
            self.data = self.data.join(data)
            self.data = self.data.fillna(method='bfill').fillna(method='ffill')
            
    def __tinkoff_stocks_parse(self, stocks_tickers : list):
        TOKEN = db.get_token(user_id=self.user_id)
        if TOKEN == None:
            TOKEN = TOKEN_SH
        data = pd.DataFrame()
        
        for name in stocks_tickers:
            figi = db.get_figi(name)
            with Client(TOKEN) as client:
                r = client.market_data.get_candles(
                    figi=figi,
                    from_=datetime.datetime(self.start_date) + datetime.timedelta(days=1),
                    to=datetime.datetime(self.end_date) + datetime.timedelta(days=1),
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
                
        
    
    def __get_overall_col_in_data(self):
        self.data['Overall'] = self.data.apply(lambda x: sum(x[name] for name in self.stocks_tickers), axis=1)
        
    def sharpe_ratio(self, rfr: float):
        # self.analysis = DataFrame: cols - stocks, row - sharpe ratio
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
        