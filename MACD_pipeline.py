import math
import time

import pandas as pd
import shift
from TraderS import TraderS
import logging as lg


from MACD_config import fast, slow, signal_period

class MACD_pipeline:

    def __init__(self,tickers):
        self.tickers = tickers
        self.df_columns = [ 'TICKER', 'LAG', 'CURRENT_PRICE','EMA_SLOW', 'EMA_FAST', 'MACD','SIGNAL_LINE','TRADE_SIGNAL','TRADE_DECISION']
        self.df = pd.DataFrame(columns=self.df_columns)
        self.df.TICKER = tickers
        lg.debug(self.df)

    def get_current_price(self):
        current_prices = {}
        for ticker in self.tickers:
            trader = TraderS.getInstance()
            current_price = trader.get_last_price(ticker)
            current_prices[ticker] = current_price
            self.update_ticker(ticker, current_price)
        lg.debug(current_prices)
        return current_prices

    def ema(self,ticker ,period, current_price, ema_type):
        beta = 1/(period + 1)
        pre_ema = self.df.loc[(self.df['TICKER'] == ticker) & (self.df['LAG'] == 0), ema_type]
        first_ema = False

        #update MACD values
        if not pre_ema.dropna().empty:
            previous_ema = pre_ema.values[0]
            current_ema = beta*current_price + (1-beta)*previous_ema
            print('current value {0} pre_ema {1}'.format(current_price,previous_ema))
        else:
            first_ema = True
            current_ema = current_price
            self.df.loc[(self.df['TICKER'] == ticker) , 'LAG'] = 0
            self.df.loc[(self.df['TICKER'] == ticker), 'CURRENT_PRICE'] = current_price
        self.df.loc[(self.df['TICKER'] == ticker) & (self.df['LAG'] == 0), ema_type] = current_ema
        if not pre_ema.dropna().empty:
            self.df.loc[(self.df['TICKER'] == ticker) & (self.df['LAG'] == 1), ema_type] = previous_ema
        return first_ema, current_ema

    def signal_line(self,ticker ,period, current_macd, ema_type):
        beta = 1/(signal_period + 1)
        first_signal ,signal_line = self.ema(ticker, signal_period, current_macd, 'SIGNAL_LINE')
        if first_signal:
            return
        trade_signal = 0
        if signal_line > current_macd:
            trade_signal = -1
            self.df.loc[(self.df['TICKER'] == ticker) & (self.df['LAG'] == 0), 'TRADE_SIGNAL'] = -1
        elif signal_line < current_macd:
            trade_signal = 1
            self.df.loc[(self.df['TICKER'] == ticker) & (self.df['LAG'] == 0), 'TRADE_SIGNAL'] = 1
        self.trade_decision(trade_signal,ticker)

    def trade_decision(self,current_trade_signal,ticker):
        beta = 1/(signal_period + 1)
        ts_p = self.df.loc[(self.df['TICKER'] == ticker) & (self.df['LAG'] == 0), 'TRADE_SIGNAL']
        previous_trade_signal = ts_p.values[0]
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
        pd.set_option('display.expand_frame_repr', False)
        while(True):
            #self.get_current_price()
            time.sleep(1)
            lg.debug('Macd running')

    def trader_disconnect(self):
        TraderS.disconnect()

    def update_ticker(self,ticker, current_price):
        first_ema , current_slow_ema = self.ema(ticker,fast, current_price, 'EMA_SLOW')
        first_ema ,current_fast_ema = self.ema(ticker,slow, current_price, 'EMA_FAST')
        if first_ema:
            return
        macd = current_fast_ema - current_slow_ema
        y1 = self.df.loc[(self.df['TICKER'] == ticker) & (self.df['LAG'] == 0), 'MACD']
        previous_macd = self.df.loc[(self.df['TICKER'] == ticker) & (self.df['LAG'] == 0), 'MACD'].values[0]
        self.df.loc[(self.df['TICKER'] == ticker) & (self.df['LAG'] == 0), 'MACD'] = macd
        x = previous_macd and not math.isnan(previous_macd)
        print('previous macd {}'.format(x))
        if x:
            self.df.loc[(self.df['TICKER'] == ticker) & (self.df['LAG'] == 1), 'MACD'] = previous_macd
            current_trade_signal = self.signal_line(ticker,signal_period,macd,'SIGNAL_LINE')


# Run the macd code
#mscd = MACD_pipeline(['SPY', 'VIXY', 'DIA', 'AAPL'])
#mscd.schedule_macd()

