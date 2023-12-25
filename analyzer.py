import pandas as pd
import numpy as np
from pandas_datareader import data as pdr
import yfinance as yfin
import datetime
from passwords import *
from functions import check_share_yahoo, check_share_moex
from dateutil.parser import parse

class Analyzer:
    def __init__(self, stocks_tickers: list, start_date : str, end_date : str, user_id: int):
        self.stocks_tickers = stocks_tickers
        self.start_date = start_date
        self.end_date = end_date
        self.user_id = user_id
        self.data = pd.DataFrame()
        self.analysis = pd.DataFrame()
        self.unable_to_parse_tickers = []
        
        self.__check_dates()
        self.__parse_all()
        
    
    def __check_dates(self):
        for date in [self.start_date, self.end_date]:
            try:
                datetime.datetime.strptime(date, '%Y-%m-%d')
            except:
                raise ValueError("Неправильно введена дата.")
    
    
    def text_analyser(self):
        res = []
        s = '<b>Результаты анализа:</b>\n\n'
        self.analysis = self.analysis.set_index('index')
        for ticker in self.stocks_tickers:
            s += f'<b>{ticker}</b>\n'
            s += f'Cumulative return: {self.analysis.loc["cumulative"][ticker].round(2)}\n'
            s += f'Standard deviation: {self.analysis.loc["std"][ticker].round(2)}\n'
            s += f'Sharpe ratio: {self.analysis.loc["sharpe"][ticker].round(2)}\n'
        res.append(s)
        if self.unable_to_parse_tickers:
            s = "<b>Не получилось собрать информацию с этих тикеров:</b>"
            for word in self.unable_to_parse_tickers:
                s += ' ' + str(word)
            res.append(s)
        else:
            res.append(None)
        return res
            
    
    def __parse_all(self):
        yahoo_tickers = []
        moex_tickers = []
        for ticker in self.stocks_tickers:
            if check_share_yahoo(ticker):
                yahoo_tickers.append(ticker)
            elif check_share_moex(ticker):
                moex_tickers.append(ticker)
            else:
                self.unable_to_parse_tickers.append(ticker)
                
        self.stocks_tickers = np.setdiff1d(self.stocks_tickers, self.unable_to_parse_tickers)
        self.stocks_tickers = list(map(lambda x: x.upper(), self.stocks_tickers))
        yahoo_tickers = list(map(lambda x: x.upper(), yahoo_tickers))
        moex_tickers = list(map(lambda x: x.upper(), moex_tickers))

        if yahoo_tickers:
            self.__yahoo_stocks_parse(yahoo_tickers)
        if moex_tickers:
            self.__moex_stocks_parse(moex_tickers)
        if moex_tickers or yahoo_tickers:
            self.__get_overall_col_in_data()
        if len(self.data) == 0:
            raise ValueError("Не получилось собрать информацию ни по одному из введенных тикеров.")
        
        
    def __yahoo_stocks_parse(self, stocks_tickers : list):
        # get not russian stocks
        # returns pd.DF: cols - [date, stocks_names...], rows - [date, stocks_price...]
        yfin.pdr_override()
        data = pdr.get_data_yahoo(stocks_tickers, start=self.start_date, end=self.end_date)['Adj Close']
        if len(stocks_tickers) == 1:
            data = data.rename(stocks_tickers[0])
        data = data.reset_index()
        data = data.set_index('Date')
        if self.data.size == 0:
            self.data = data.fillna(method='bfill').fillna(method='ffill')
        else:
            self.data = self.data.join(data)
            self.data = self.data.fillna(method='bfill').fillna(method='ffill')
            
            
    def __moex_stocks_parse(self, stocks_tickers : list):
        data = pd.DataFrame()
        
        for ticker in stocks_tickers:
            query = f'http://iss.moex.com/iss/engines/stock/markets/shares/securities/{ticker}/candles.csv?from={self.start_date}&till={self.end_date}&interval=24'
            df = pd.read_csv(query, sep=';', header=1)
            df['Date'] = df['begin'].apply(lambda x: parse(x))
            df = df.set_index('Date')['close']
            data[ticker] = df
            
        if self.data.size == 0:
            self.data = data.fillna(method='bfill').fillna(method='ffill')
        else:
            self.data = self.data.join(data)
            self.data = self.data.fillna(method='bfill').fillna(method='ffill')
                
        
    def __get_overall_col_in_data(self):
        self.data['Overall'] = self.data.apply(lambda x: sum(x[name] for name in self.stocks_tickers), axis=1)
        
        
    def sharpe_ratio(self, rfr=0.02):
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
            




