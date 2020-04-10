import getopt
import math
import sys
import time
from typing import List

import pandas as pd
import numpy
import shift
from TraderS import TraderS
import logger
import logging as lg

# import goodcbfs
from credentials import my_password, my_username


class get_best_price_dataframe():
    def __init__(self, tickers):
        self.tickers = tickers
        # self.df_columns = ['TICKER', 'LAG', 'BEST_PRICE']
        self.df = pd.DataFrame(columns=['TICKER', 'LAG', 'BEST_PRICE'])
        lg.debug(self.df)

    def get_best_price_dataframe(self):
        best_prices = {}
        lag = 1
        for ticker in self.tickers:
            trader = TraderS.getInstance()
            best_price = trader.get_last_price(ticker)
            best_prices[ticker]  = best_price
            self.update_ticker(ticker, best_price)
        else:
            lag += 1
        lg.debug(best_prices)
        self.df.append

    def get_best_price_dataframe(self):
        best_prices = {}
        lag = 1
        for ticker in self.tickers:
            trader = TraderS.getInstance()
            best_price = trader.get_last_price(ticker)
            best_prices[ticker]  = best_price
            self.update_ticker(ticker, best_price)
        else:
            lag += 1
        lg.debug(best_prices)
        self.df.append



if __name__=="__main__":
    lg.debug("App Started")
    try:
        trader = TraderS.getInstance()
        trader.sub_all_order_book()
        time.sleep(5)
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