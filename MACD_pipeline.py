import getopt
import math
import sys
import time
import MACD_config
from typing import List

import pandas as pd
import numpy
import shift
from TraderS import TraderS


from MACD_config import fast, slow, signal_period

class MACD_pipeline:

    def __init__(self,tickers):
        self.tickers = tickers
        self.df_columns = [ 'TICKER', 'LAG', 'CURRENT_PRICE','EMA_SLOW', 'EMA_FAST', 'MACD','SIGNAL_LINE','TRADE_SIGNAL','TRADE_DECISION']
        self.df = pd.DataFrame(columns=self.df_columns)
        self.df.TICKER = tickers
        print(self.df)

    def get_current_price(self):
        current_prices = {}
        for ticker in self.tickers:
            trader = TraderS.getInstance()
            current_price = trader.get_last_price(ticker)
            current_prices[ticker] = current_price
            self.update_ticker(ticker, current_price)

        return current_prices

    def ema(self,ticker ,period, current_price, ema_type):
        beta = 1/(period + 1)
        previous_ema = self.df.loc[(self.df['TICKER']  == ticker) & (self.df['LAG'] == 0) , ema_type]
        #self.df.loc[self.df['TICKER'] == 'AAPL', ['LAG']] = 0
        print(previous_ema)

        #update MACD values
        if len(previous_ema) > 0 :
            current_ema = beta*current_price + (1-beta)*previous_ema
        else:
            current_ema = current_price
            self.df.loc[(self.df['TICKER'] == ticker) , 'LAG'] = 0
            self.df.loc[(self.df['TICKER'] == ticker), 'CURRENT_PRICE'] = current_price
        self.df.loc[(self.df['TICKER'] == ticker) & (self.df['LAG'] == 0), ema_type] = current_ema
        self.df.loc[(self.df['TICKER'] == ticker) & (self.df['LAG'] == 1), ema_type] = previous_ema
        print(self.df.head())
        return current_ema

    def signal_line(self,ticker ,period, current_macd, ema_type):
        beta = 1/(signal_period + 1)
        signal_line = self.ema(ticker, signal_period, current_macd, 'SIGNAL_LINE')
        trade_signal = signal_line > current_macd
        if trade_signal:
            self.df.loc[(self.df['TICKER'] == ticker) & (self.df['LAG'] == 0), 'TRADE_SIGNAL'] = -1
        else:
            self.df.loc[(self.df['TICKER'] == ticker) & (self.df['LAG'] == 0), 'TRADE_SIGNAL'] = 1
        print(self.df)
        self.trade_decision(trade_signal,ticker)

    def trade_decision(self,current_trade_signal,ticker):
        beta = 1/(signal_period + 1)
        previous_trade_signal = self.df.loc[(self.df['TICKER'] == ticker) & (self.df['LAG'] == 0), 'TRADE_SIGNAL']
        if current_trade_signal > previous_trade_signal:
            # Buy the stocks
            ticker_buy = shift.Order(shift.Order.Type.MARKET_BUY, ticker, 20)
            TraderS.getInstance.submit_order(ticker_buy)
            self.df.loc[(self.df['TICKER'] == ticker) & (self.df['LAG'] == 0), 'TRADE_DECISION'] = 1
            print('Buy the stock {0}'.format(ticker))
        elif current_trade_signal < previous_trade_signal:
            # Sell the stocks
            ticker_sell = shift.Order(shift.Order.Type.MARKET_SELL, ticker, 20)
            TraderS.getInstance.submit_order(ticker_sell)
            self.df.loc[(self.df['TICKER'] == ticker) & (self.df['LAG'] == 0), 'TRADE_DECISION'] = -1
            print('Sell the stock {0}'.format(ticker))
        else:
            print('No Buy Sell')
        print(self.df)


    def schedule_macd(self):
        while(True):
            self.get_current_price()
            time.sleep(1)
    def trader_disconnect(self):
        TraderS.disconnect()

    def update_ticker(self,ticker, current_price):
        current_slow_ema = self.ema(ticker,fast, current_price, 'EMA_SLOW')
        current_fast_ema = self.ema(ticker,slow, current_price, 'EMA_FAST')
        macd = current_fast_ema - current_slow_ema
        previous_macd = self.df.loc[(self.df['TICKER'] == ticker) & (self.df['LAG'] == 0), 'MACD']
        self.df.loc[(self.df['TICKER'] == ticker) & (self.df['LAG'] == 0), 'MACD'] = macd
        self.df.loc[(self.df['TICKER'] == ticker) & (self.df['LAG'] == 1), 'MACD'] = previous_macd

        current_trade_signal = self.signal_line(ticker,signal_period,macd,'SIGNAL_LINE')


# Run the macd code
mscd = MACD_pipeline(['SPY', 'VIXY', 'DIA', 'AAPL'])
mscd.schedule_macd()

