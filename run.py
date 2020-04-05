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

# import goodcbfs
from credentials import my_password, my_username

def get_initialprice(trader, tickers):
    # Getting the initial price recorded at 1st sec of trading
    initial_price = {}
    for j, k in enumerate(tickers):
        initial_price[k] = trader.get_last_price(k)
    lg.debug(initial_price)
    return initial_price

def get_volatility(trader):
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

def trading_symbols(vol):
    lg.debug('trading_symbols  :' + str(vol))
    vol_tickers= []
    for key, value in vol.items():
        if value > 0.00015:
            vol_tickers.append(key)
    lg.debug('Greater than  :' + str(vol_tickers))
    return vol_tickers

def filter_tickers_buy_lastPrice(initial_price_tickers, volatility, trader):
    lg.debug('filter_tickers_lastPrice :' + str(initial_price_tickers))
    fil_tickers= []
    for v_ticker in volatility:
        last_price = trader.get_last_price(v_ticker)
        if last_price > initial_price_tickers.get(v_ticker):
            fil_tickers.append(v_ticker)
    lg.debug('filtered ticker last price greater than initial price:' + str(fil_tickers))
    return fil_tickers

def filter_tickers_sell_lastPrice(initial_price_tickers, volatility, trader):
    lg.debug('filter_tickers_lastPrice :' + str(initial_price_tickers))
    fil_tickers= []
    for v_ticker in volatility:
        last_price = trader.get_last_price(v_ticker)
        if last_price < initial_price_tickers.get(v_ticker):
            fil_tickers.append(v_ticker)
    lg.debug('filtered ticker last price less than initial price:' + str(fil_tickers))
    return fil_tickers


def buy_ticker( trader: shift.Trader, tickers):
    lg.debug('buy_tickers :'+ str(tickers))
    for ticker in tickers:
       ticker_buy = shift.Order(shift.Order.Type.MARKET_BUY, ticker, 10)
       trader.submit_order(ticker_buy)
       lg.debug('ticker bought:' + str(ticker))
    if len(tickers)==0:
        ticker_buy = shift.Order(shift.Order.Type.MARKET_BUY, 'VIXY', 40)
        trader.submit_order(ticker_buy)


def sell_ticker( trader: shift.Trader, tickers):
    lg.debug('sell_tickers :' + str(tickers))
    for ticker in tickers:
       ticker_sell = shift.Order(shift.Order.Type.MARKET_SELL, ticker, 10)
       trader.submit_order(ticker_sell)
       print('ticker sold:' + str(ticker))

def init_tickers():
    # get the ticker's list
    tickers = trader.get_stock_list()
    tickers.remove('DIA')
    tickers.remove('SPY')
    tickers.remove('VIXY')
    lg.debug(tickers)
    return tickers

def demo_09(trader: shift.Trader):
    """
    This method prints all submitted orders information.
    :param trader:
    :return:
    """

    print(
        "Symbol\t\t\t\tType\t  Price\t\tSize\tExecuted\tID\t\t\t\t\t\t\t\t\t\t\t\t\t\t Status\t\tTimestamp"
    )
    for order in trader.get_submitted_orders():
        if order.status == shift.Order.Status.FILLED:
            price = order.executed_price
        else:
            price = order.price
        print(
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

if __name__=="__main__":
    lg.debug("App Started")
    try:
        # create trader object
        trader = shift.Trader(my_username)
        # connection & subs to order_book
        trader.connect("initiator.cfg", my_password)
        trader.sub_all_order_book()
        time.sleep(5)
        # Run the macd code
        # mscd = MACD_pipeline(['SPY', 'VIXY', 'DIA', 'AAPL'])
        # mscd.schedule_macd()
        # mscd.trader_disconnect()

        tickers = init_tickers()
        time.sleep(5)
        while(True):
            # get the initial price for all tickers
            intial_price = get_initialprice(trader, tickers)
            # get the volatility for 1st 15 mins of trading window
            vol_tickers = get_volatility(trader)
            thres_tickers = trading_symbols(vol_tickers)
            thrs_grter_ticker = filter_tickers_buy_lastPrice(intial_price, thres_tickers, trader)
            buy_ticker(trader, thrs_grter_ticker)
            thrs_less_ticker = filter_tickers_sell_lastPrice(intial_price, thres_tickers, trader)
            sell_ticker(trader,thrs_less_ticker)
            time.sleep(900)
            sell_ticker(trader,thrs_grter_ticker)
            buy_ticker(trader,thrs_less_ticker)
            demo_09(trader)



    except shift.IncorrectPasswordError as e:
        lg.debug(e)
        sys.exit(2)
    except shift.ConnectionTimeoutError as e:
        lg.debug(e)
        sys.exit(2)
    except Exception as err:
        lg.error("Fatal error in main loop", exc_info = True)
    finally:
        trader.disconnect()
        lg.debug('Trader connection disconnected')
