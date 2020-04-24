import getopt
import math
import sys
import time
from typing import List

import numpy as np
import pandas as pd
import numpy
import shift
from TraderS import TraderS
import logger
import logging as lg
from datetime import datetime
from logger import init

# import goodcbfs
from credentials import my_password, my_username


class get_last_price_dataframe:
    def __init__(self):
        self.tickers = None
        self.df = pd.DataFrame(columns=['TIME','TICKER','BEST_PRICE'])
        # self.df.TICKER = tickers
        # self.df.TIME = now = datetime.now().time()
        lg.debug(self.df)

    def init_tickers(self):
        # get the ticker's list
        tickers = TraderS.getInstance().get_stock_list()
        lg.debug(tickers)
        self.tickers = tickers

    def update_ticker(self, ticker, current_price):
        self.current_data = {'TIME': [datetime.now().time()] , 'TICKER': '', 'BEST_PRICE': np.NaN}
        self.current_data['BEST_PRICE'] = [current_price]
        self.current_data['TICKER'] = [ticker]
        lg.debug(self.current_data)
        return self.current_data

    def get_price_dataframe(self):
        last_prices = {}
        for ticker in self.tickers:
            trader = TraderS.getInstance()
            last_price = trader.get_last_price(ticker)
            last_prices[ticker]  = last_price
            self.update_ticker(ticker, last_price)
            self.df = pd.concat([pd.DataFrame.from_dict(self.current_data),self.df],ignore_index=True)
        lg.debug(self.df)
        return self.df


def demo_07(trader: shift.Trader):
    """
    This method provides information on the structure of PortfolioSummary and PortfolioItem objects:
     get_portfolio_summary() returns a PortfolioSummary object with the following data:
     1. Total Buying Power (get_total_bp())
     2. Total Shares (get_total_shares())
     3. Total Realized Profit/Loss (get_total_realized_pl())
     4. Timestamp of Last Update (get_timestamp())

     get_portfolio_items() returns a dictionary with "symbol" as keys and PortfolioItem as values,
     with each providing the following information:
     1. Symbol (get_symbol())
     2. Shares (get_shares())
     3. Price (get_price())
     4. Realized Profit/Loss (get_realized_pl())
     5. Timestamp of Last Update (get_timestamp())
    :param trader:
    :return:
    """
    #
    # print("Buying Power\tTotal Shares\tTotal P&L\tTimestamp")
    # print(
    #     "%12.2f\t%12d\t%9.2f\t%26s"
    #     % (
    #         trader.get_portfolio_summary().get_total_bp(),
    #         trader.get_portfolio_summary().get_total_shares(),
    #         trader.get_portfolio_summary().get_total_realized_pl(),
    #         trader.get_portfolio_summary().get_timestamp(),
    #     )
    # )

    print()

    print("Symbol\t\tShares\t\tPrice\t\t  P&L\tTimestamp")
    for item in trader.get_portfolio_items().values():
        print(
            "%6s\t\t%6d\t%9.2f\t%9.2f\t%26s"
            % (
                item.get_symbol(),
                item.get_shares(),
                item.get_price(),
                item.get_realized_pl(),
                item.get_timestamp(),
            )
        )

    return


if __name__=="__main__":
    init()
    lg.debug("App Started")
    try:
        trader = TraderS.getInstance()
        trader.sub_all_order_book()
        time.sleep(5)
        # price_collection = get_last_price_dataframe()
        # price_collection.init_tickers()
        ticker_buy = shift.Order(shift.Order.Type.MARKET_BUY, 'CS1', 1)
        trader.submit_order(ticker_buy)
        ticker_sell = shift.Order(shift.Order.Type.MARKET_SELL, 'CS2', 1)
        trader.submit_order(ticker_sell)
        time.sleep(30)
        demo_07(trader)
        time.sleep(10)
        for item in trader.get_portfolio_items().values():
            symbol, shares = item.get_symbol(), item.get_shares()
            lg.debug(symbol)
            lg.debug(shares)
            if shares > 0:
                ticker_sell = shift.Order(shift.Order.Type.MARKET_SELL, symbol, shares//100)
                trader.submit_order(ticker_sell)
            else:
                ticker_buy = shift.Order(shift.Order.Type.MARKET_BUY, 'CS2', 100)
                trader.submit_order(ticker_buy)
        time.sleep(60)
        demo_07(trader)
        # while True:
        #     get_prices = price_collection.get_price_dataframe()
        #     time.sleep(60)
        # get_prices.to_csv('out.csv')
    except shift.IncorrectPasswordError as e:
        lg.debug(e)
        sys.exit(2)
    except shift.ConnectionTimeoutError as e:
        lg.debug(e)
        sys.exit(2)
    except Exception as err:
        lg.error("Fatal error in main loop", exc_info = True)
    except:
        lg.error("Fatal error in main loop", exc_info=True)
    finally:
        trader.disconnect()
        lg.debug('Trader connection disconnected')