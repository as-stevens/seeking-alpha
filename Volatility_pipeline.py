import getopt
import math
import sys
import time
from typing import List

import pandas as pd
import numpy
import shift
# import MACD_pipeline
import logger
import logging as lg
from TraderS import TraderS

# import goodcbfs
from credentials import my_password, my_username
class Volatility_Pipeline:
    def get_initialprice(self,trader,tickers):
        # Getting the initial price recorded at 1st sec of trading
        initial_price = {}
        for j, k in enumerate(tickers):
            initial_price[k] = trader.get_last_price(k)
        lg.debug(initial_price)
        return initial_price

    def get_volatility(self,trader,tickers):
        # get last trading price for all tickers at an interval of 1 min for 1st 15 mins
        trader.request_sample_prices(tickers, sampling_frequency=1, sampling_window=300)
        lg.debug('Initiate call to trader.request_sample_prices')
        time.sleep(301)
        lg.debug('returned  from trader.request_sample_prices')
        vol = {}
        for i, s in enumerate(tickers):
            stock_ticker = s
            #log_returns = trader.get_last_price(stock_ticker)
            log_returns = trader.get_log_returns(stock_ticker)
            lg.debug('Log return : '+str(log_returns))
            if log_returns:
                log_returns_sq = [j**2 for j in log_returns]
                #log_returns_sq = [log_returns ** 2]
                log_returns_size = trader.get_log_returns_size(stock_ticker)
                total = 0
                for ele in range(0,len(log_returns_sq)):
                    total = total + log_returns_sq[ele]
                vol[s] = (((1 / log_returns_size) * total)**0.5)
        lg.debug('returned  get_volatility :'+ str(vol))
        return vol

    def filterticker_on_threshold(self, vol):
        lg.debug('trading_symbols  :' + str(vol))
        vol_tickers= []
        for key, value in vol.items():
            if value > 0.00012:
                vol_tickers.append(key)
        lg.debug('Greater than  :' + str(vol_tickers))
        return vol_tickers

    def filter_tickers_lastPrice(self, initial_price_tickers, volatility, trader):
        lg.debug(str(initial_price_tickers))
        buy_tickers= []
        sell_tickers = []
        for v_ticker in volatility:
            last_price = trader.get_last_price(v_ticker)
            if last_price > initial_price_tickers.get(v_ticker):
                buy_tickers.append(v_ticker)
            elif last_price < initial_price_tickers.get(v_ticker):
                sell_tickers.append(v_ticker)
        # if the len of buy_tickers > 3, replace all trades with buy -> SPY and sell -> VIXY
        if len(buy_tickers) > 3:
            buy_tickers = []
            sell_tickers = []
            buy_tickers.append('SPY')
            sell_tickers.append('VIXY')
        lg.debug('ticker last price less than initial price:' + str(sell_tickers))
        lg.debug('ticker last price greater than initial price:' + str(buy_tickers))
        return buy_tickers,sell_tickers

    def add_VIXY(self, buy_tickers,sell_tickers):
        buy_tickers = [i for i in buy_tickers if i]
        sell_tickers = [i for i in sell_tickers if i]
        tickers = []
        tickers.extend(buy_tickers)
        tickers.extend(sell_tickers)
        lg.debug('Buy/Sell tickers' + str(tickers))
        if len(tickers) > 0:
            if tickers.__contains__('SPY'):
                return buy_tickers, 13 , 100
            else:
                return buy_tickers, 10 , 10
        else:
            return ['VIXY'], 200 , 200


    def buy_ticker(self, trader: shift.Trader, tickers,buy_order_size):
        lg.debug('buy_tickers :' + str(tickers))
        for ticker in tickers:
           ticker_buy = shift.Order(shift.Order.Type.MARKET_BUY, ticker, buy_order_size)
           trader.submit_order(ticker_buy)
           lg.debug('ticker bought:' + str(ticker))

    def sell_ticker( self, trader: shift.Trader, tickers, sell_order_size):
        lg.debug('sell_tickers :' + str(tickers))
        for ticker in tickers:
            # if ticker == 'VIXY':
            #     order_size = 100
            ticker_sell = shift.Order(shift.Order.Type.MARKET_SELL, ticker, sell_order_size)
            trader.submit_order(ticker_sell)
            lg.debug('ticker sold:' + str(ticker))

    def init_tickers(self,trader):
        # get the ticker's list
        tickers = trader.get_stock_list()
        tickers.remove('DIA')
        tickers.remove('SPY')
        tickers.remove('VIXY')
        lg.debug(tickers)
        return tickers

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

# connect


    # connect
    def schedule(self):
        lg.debug('Volatility Algo started')
        while (True):
            # get the initial price for all tickers
            trader = TraderS.getInstance()
            tickers = self.init_tickers(trader)
            intial_price = self.get_initialprice(trader, tickers)
            # get the volatility for 1st 15 mins of trading window
            vol_tickers = self.get_volatility(trader,tickers)
            threshold_tickers = self.filterticker_on_threshold(vol_tickers)
            buyticker, sellticker = self.filter_tickers_lastPrice(intial_price, threshold_tickers, trader)
            buyticker, buy_order_size, sell_order_size  = self.add_VIXY(buyticker, sellticker)
            self.buy_ticker(trader, buyticker, buy_order_size)
            self.sell_ticker(trader, sellticker, sell_order_size)
            time.sleep(720)
            self.sell_ticker(trader, buyticker, buy_order_size)
            self.buy_ticker(trader, sellticker, sell_order_size)
            self.demo_09(trader)