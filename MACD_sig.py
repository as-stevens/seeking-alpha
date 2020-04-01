import getopt
import math
import sys
import time
import MACD_config
from typing import List

import pandas as pd
import numpy
import shift

def EMA(self,n,ticker):
    # current price, ticker , window, last_batch_data
    # current price -> trader
    # window -> function parameter
    # ticker -> function parmater
    # laste_batch_data -> ?

    # pipeline tickers-> ticker_queue ->current_price -> ema -> macd-> signal-> buy/sell 2- repreat interval 1 sec
    # 1) tickers = few selected tickers
    # 2) buy and sell signal lines
    # signals - classify -> buy or sell
    # trade -> trade the ticker
    #3) tader -> current_price
    #4) ema : fast(3 seconds) and slow (10 seconds)
    #5) macd -> fast_ema -slow ema -> continous data-
    # 6) signal data : e_macd -> ema of macd for window of (9 seconds) -> continious data
    # 7) 19th second first signal data : macd - first signal at 19 second
    # and it will continue for rest of the day
    # previous values before signal -> macd < signal data -> buy
    # else sell
    #8) if at end of day any open positions then it should be sold

    B = 2 / (n + 1)
    # BAC$EMA_12[t + 1] = BAC_price[t + 1] * BS + (1 - BS) * BAC$EMA_12[t]





def MACD(self,ticker):
    fast = ''
    slow = ''
    # calculate the slow ema value for a ticker
    slow_ema = EMA(ticker,slow)
    # calculate the slow ema value for a ticker
    fast_ema = EMA(ticker, fast)
    # calculate the macd of the ticker
    macd = fast_ema - slow_ema


def signal_line(self,macd):
    signal_period = ''
    signal_indcator = self.EMA(macd)

