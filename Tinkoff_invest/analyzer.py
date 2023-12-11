import pandas as pd
import numpy as np
from pandas_datareader import data as pdr
import yfinance as yfin

class Analyzer:
    def __init__(self, stocks_names: list, stocks_figi: list, start_date : str, end_date : str):
        self.stocks_names = stocks_names
        self.stocks_figi = stocks_figi
        self.start_date = start_date
        self.end_date = end_date
        self.data = pd.DataFrame()
        self.analysis = pd.DataFrame()
        
    def yahoo_stocks_parse(self, stocks_names : list, start_date : str, end_date : str):
        # get not russian stocks
        # returns pd.DF: cols - [date, stocks_names...], rows - [date, stocks_price...]
        yfin.pdr_override()
        data = pdr.get_data_yahoo(stocks_names, start=start_date, end=end_date)['Adj Close']
        if self.data.size == 0:
            self.data = data
        else:
            self.data.join(data, on='date')
    
    def get_overall_col_in_data(self):
        self.data['Overall'] = self.data.apply(lambda x: sum(x[name] for name in self.stocks_names), axis=1)
        
    def sharpe_ratio(self, rfr: float):
        # returns DataFrame: cols - stocks, row - sharpe ratio
        std = self.data[self.stocks_names].apply(lambda x: x.pct_change().std() * np.sqrt(len(self.data)))
        cumulative = self.data[self.stocks_names].apply(lambda x: (x[len(self.data) - 1] / x[0]) - 1)
        sharpe = (cumulative - rfr) / std
        
        analysis = pd.DataFrame([std, cumulative, sharpe])
        analysis['index'] = ['std', 'cumulative', 'sharpe']
        if self.analysis.size == 0:
            self.analysis = analysis
            return
        
        indexes = np.setdiff1d(analysis['index'], self.analysis['index'])
        for i in indexes:
            self.analysis = pd.concat([self.analysis, analysis[analysis['index'] == i]])
        
# anal = Analyzer(['AAPL', 'TSLA'], [], '2022-01-01', '2023-01-01')
# anal.yahoo_stocks_parse(anal.stocks_names, anal.start_date, anal.end_date)
# anal.get_overall_col_in_data()
# anal.sharpe_ratio(0.02)
# print(anal.analysis)
# anal.sharpe_ratio(0.02)
# print(anal.analysis)
        