import getopt
import math
import sys
import time
import MACD_config
from typing import List

import pandas as pd
import numpy
import shift
import Trader

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import FeatureUnion, Pipeline

from MACD_config import fast, slow, signal_period

class MACD_pipeline(TransformerMixin):

    def __init__(self,tickers, trader='',):
        self.tickers = tickers
        self.trader = trader
        self.df_columns = [ 'TICKER', 'LAG', 'CURRENT_PRICE','EMA_SLOW', 'EMA_FAST', 'MACD' ]
        self.df = pd.DataFrame(columns=self.df_columns)
        self.df.TICKER = tickers
        print(self.df)

    def get_current_price(self):
        current_prices = {}
        for ticker in self.tickers:
            trader = Trader.getInstance()
            current_price = trader.get_current_price(ticker)
            current_prices[ticker] = current_price
            self.update_ticker(ticker, current_price)

        return current_prices

    def ema(self,ticker ,period, current_price, ema_type):
        beta = 1/(period + 1)
        previous_ema = self.df.loc[(self.df['TICKER']  == ticker) & (self.df['LAG'] == 0) , ema_type]
        #self.df.loc[self.df['TICKER'] == 'AAPL', ['LAG']] = 0

        #update MACD values
        current_ema = beta*current_price + (1-beta)*previous_ema
        self.df.loc[(self.df['TICKER'] == ticker) & (self.df['LAG'] == 0), ema_type] = current_ema
        self.df.loc[(self.df['TICKER'] == ticker) & (self.df['LAG'] == 1), ema_type] = previous_ema
        return current_ema

    def schedule_macd(self):
        while(True):
            self.get_current_price()
            time.sleep(1)

    def update_ticker(self,ticker, current_price):
        current_slow_ema = self.ema(ticker,fast, current_price, 'EMA_SLOW')
        current_fast_ema = self.ema(ticker,slow, current_price, 'EMA_FAST')
        macd = current_fast_ema - current_slow_ema
        previous_macd = self.df.loc[(self.df['TICKER'] == ticker) & (self.df['LAG'] == 0), 'MACD']
        self.df.loc[(self.df['TICKER'] == ticker) & (self.df['LAG'] == 0), 'MACD'] = macd
        self.df.loc[(self.df['TICKER'] == ticker) & (self.df['LAG'] == 1), 'MACD'] = previous_macd

        self.macd(ticker,signal_period)


mscd = MACD_pipeline(tickers=['AAPL','AMN'])
mscd.schedule_macd()


