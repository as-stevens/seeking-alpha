import getopt
import math
import sys
import time
from typing import List

import pandas as pd
import numpy
import shift

# import goodcbfs
from credentials import my_password, my_username

def get_initialprice(trader, tickers):
    # Getting the initial price recorded at 1st sec of trading
    initial_price = {}
    for j, k in enumerate(tickers):
        initial_price[k] = trader.get_last_price(k)
    print('initial_price' + str(initial_price))
    return initial_price

def get_volatility(trader):
    # get last trading price for all tickers at an interval of 1 min for 1st 15 mins
    trader.request_sample_prices(tickers, sampling_frequency=1, sampling_window=300)
    print('Initiate call to trader.request_sample_prices')
    time.sleep(301)
    print('returned  from trader.request_sample_prices')
    vol = {}
    for i, s in enumerate(tickers):
        stock_ticker = s
        #log_returns = trader.get_last_price(stock_ticker)
        log_returns = trader.get_log_returns(stock_ticker)
        print('Log return : '+str(log_returns))
        if log_returns:
            log_returns_sq = [j**2 for j in log_returns]
            #log_returns_sq = [log_returns ** 2]
            log_returns_size = trader.get_log_returns_size(stock_ticker)
            total = 0
            for ele in range(0,len(log_returns_sq)):
                total = total + log_returns_sq[ele]
            vol[s] = (((1 / log_returns_size) * total)**0.5)
    print('returned  get_volatility :'+ str(vol))
    return vol

def trading_symbols(vol):
    vol_tickers= []
    for v_ticker in vol.values():
        if v_ticker > 0.00015:
            vol_tickers.append(v_ticker)
    return vol_tickers

def filter_tickers_lastPrice(initial_price_tickers, volatility, trader):
    fil_tickers= []
    for v_ticker in volatility:
        last_price = trader.get_last_price(v_ticker)
        if last_price > initial_price_tickers.get(v_ticker):
            fil_tickers.append(v_ticker)
    return fil_tickers


def buy_ticker( trader: shift.Trader, tickers):
   for ticker in tickers:
       ticker_buy = shift.Order(shift.Order.Type.MARKET_BUY, ticker, 50)
       trader.submit_order(ticker_buy)

def sell_ticker( trader: shift.Trader, tickers):
   for ticker in tickers:
       ticker_buy = shift.Order(shift.Order.Type.MARKET_BUY, ticker, 50)
       trader.submit_order(ticker_buy)

def init_tickers():
    # get the ticker's list
    tickers = trader.get_stock_list()
    tickers.remove('DIA')
    tickers.remove('SPY')
    tickers.remove('VIXY')
    print(tickers)
    return tickers


    #     best_bid = trader.get_best_price(stock_ticker).get_bid_price()
    #     print(best_bid)
    #     print('best bid  value '+s+'## ' + str(best_bid))
    #     best_ask = trader.get_best_price(stock_ticker).get_ask_price()
    #     print('best bid  value ' + s + '## ' + str(best_bid))
    #     print('best ask  value ##' + str(best_ask))

# connect
try:
    # create trader object
    trader = shift.Trader(my_username)
    # connection & subs to order_book
    trader.connect("initiator.cfg", my_password)
    trader.sub_all_order_book()
    tickers = init_tickers()
    time.sleep(5)
    # print(trader.get_last_price('AAPL'))
    # get the initial price for all tickers
    intial_price = get_initialprice(trader, tickers)
    # get the volatility for 1st 15 mins of trading window
    vol_tickers = get_volatility(trader)
    thres_tickers = trading_symbols(vol_tickers)
    thrs_grter_ticker = filter_tickers_lastPrice(intial_price,thres_tickers,trader)
    buy_ticker(trader,thrs_grter_ticker)

except shift.IncorrectPasswordError as e:
    print(e)
    #sys.exit(2)
except shift.ConnectionTimeoutError as e:
    print(e)
    #sys.exit(2)
finally:
    trader.disconnect()
    print('Trader connection disconnected')


