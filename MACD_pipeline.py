import math
import time
from datetime import datetime
from logger import init
import pandas as pd
import shift
from TraderS import TraderS
import logging as lg
from numpy import nan


from MACD_config import fast, slow, signal_period

class MACD_pipeline:

    def __init__(self,tickers):
        self.tickers = tickers
        self.df_columns = [ 'TIME', 'TICKER', 'CURRENT_PRICE','EMA_SLOW', 'EMA_FAST', 'MACD','SIGNAL_LINE','TRADE_SIGNAL','TRADE_DECISION']
        #self.df_pre = pd.DataFrame(columns=self.df_columns)
        self.df_current = pd.DataFrame(columns=self.df_columns)
        self.df_current.TICKER = tickers
        self.df_current.TIME = now = datetime.now().time()

        lg.debug(self.df_current)

    def demo_09(self, trader: shift.Trader):
        """
        This method prints all submitted orders information.
        :param trader:
        :return:
        """

        lg.debug(
            "Symbol\t\t\t\tType\t  Price\t\tSize\tExecuted\tID\t\t\t\t\t\t\t\t\t\t\t\t\t\t Status\t\tTimestamp"
        )
        for order in trader.get_submitted_orders():
            if order.status == shift.Order.Status.FILLED:
                price = order.executed_price
            else:
                price = order.price
            lg.debug(
                "%6s\t%16s\t%7.2f\t\t%4d\t\t%4d\t%36s\t%23s\t\t%26s"
                % (
                    order.symbol,
                    order.type,
                    price,
                    order.size,
                    order.executed_size,
                    order.id,
                    order.status,
                    order.timestamp,
                )
            )

        return


    def get_current_price(self):
        current_prices = {}
        for ticker in self.tickers:
            trader = TraderS.getInstance()
            current_price = trader.get_last_price(ticker)
            current_prices[ticker] = current_price
            self.update_ticker(ticker, current_price)
            df = pd.DataFrame(self.current_data, index=[0])
            self.df_current = pd.concat([self.df_current, df])
        lg.debug(self.df_current.head(10))
        lg.debug(current_prices)
        return current_prices

    def ema(self,period, current_price, ema_val):
        beta = 1/(period + 1)
        first_ema = False

        #update MACD values
        if ema_val and not math.isnan(ema_val):
            previous_ema = ema_val
            current_ema = beta*current_price + (1-beta)*previous_ema
            lg.debug('current value {0} pre_ema {1}'.format(current_price,previous_ema))
        else:
            first_ema = True
            current_ema = current_price
        return first_ema, current_ema

    def signal_line(self ,period, current_macd, last_record):
        sig_line = last_record.get('SIGNAL_LINE')
        first_signal ,signal_line = self.ema(period, current_macd, sig_line)
        if first_signal:
            self.current_data['SIGNAL_LINE'] = current_macd
            return
        trade_signal = 0
        self.current_data['SIGNAL_LINE'] = signal_line
        if signal_line > current_macd:
            trade_signal = -1
            self.current_data['TRADE_SIGNAL'] = -1
        elif signal_line < current_macd:
            trade_signal = 1
            self.current_data['TRADE_SIGNAL'] = 1
        self.trade_decision(trade_signal,last_record)

    def trade_decision(self,current_trade_signal,last_record):
        ticker = last_record.get('TICKER')
        beta = 1/(signal_period + 1)
        previous_trade_signal = last_record.get('TRADE_SIGNAL')
        if math.isnan(previous_trade_signal):
            self.current_data['TRADE_SIGNAL'] = current_trade_signal
            return
        if current_trade_signal < previous_trade_signal:
            # Buy the stocks
            ticker_buy = shift.Order(shift.Order.Type.MARKET_BUY, ticker, 20)
            TraderS.getInstance().submit_order(ticker_buy)
            self.current_data['TRADE_DECISION'] = 1
            lg.debug('Buy the stock {0}'.format(ticker))
        elif current_trade_signal > previous_trade_signal:
            # Sell the stocks
            ticker_sell = shift.Order(shift.Order.Type.MARKET_SELL, ticker, 20)
            TraderS.getInstance().submit_order(ticker_sell)
            self.current_data['TRADE_DECISION'] = -1
            lg.debug('Sell the stock {0}'.format(ticker))
        else:
            lg.debug('No Buy Sell')
        #lg.debug(self.df_current)

    def schedule_macd(self):
        pd.set_option('display.expand_frame_repr', False)
        self.trade()
        time.sleep(12600)
        self.trade()

    def trade(self):
        start_time = time.time()
        elapsed_time = time.time() - start_time
        while (elapsed_time < 5400):
            self.get_current_price()
            time.sleep(30)
            self.demo_09(TraderS.getInstance())
            elapsed_time = time.time() - start_time

    def trader_disconnect(self):
        TraderS.disconnect()

    def update_ticker(self, ticker, current_price):
        self.current_data = {'TIME': datetime.now().time() , 'TICKER': '', 'CURRENT_PRICE': nan,'EMA_SLOW' : nan, 'EMA_FAST': nan, 'MACD': nan,'SIGNAL_LINE': nan,'TRADE_SIGNAL': nan,'TRADE_DECISION': nan}
        self.current_data['CURRENT_PRICE'] = current_price
        self.current_data['TICKER'] = ticker
        tic = self.df_current.loc[(self.df_current['TICKER'] == ticker)]
        last_record = self.df_current.loc[(self.df_current['TICKER'] == ticker)].sort_values(by=['TIME'], ascending=False).head(1)
        last_record = last_record.iloc[0]
        pre_slow_ema = last_record.get('EMA_SLOW')
        first_ema, current_slow_ema = self.ema(slow, current_price, pre_slow_ema)
        self.current_data['EMA_SLOW'] = current_slow_ema
        if first_ema:
            return
        pre_fast_ema = last_record.get('EMA_FAST')
        first_ema, current_fast_ema = self.ema(fast, current_price, pre_fast_ema)
        self.current_data['EMA_FAST'] = current_fast_ema
        if first_ema:
            return

        macd = current_fast_ema - current_slow_ema
        self.current_data['MACD'] = macd
        previous_macd = last_record.get('MACD')
        lg.debug('previous macd {}'.format(previous_macd))
        if previous_macd:
            current_trade_signal = self.signal_line(signal_period,macd,last_record)


# Run the macd code
# init()
# mscd = MACD_pipeline(['SPY', 'VIXY', 'DIA', 'AAPL'])
# TraderS.getInstance().sub_all_order_book()
# time.sleep(5)
# mscd.schedule_macd()

