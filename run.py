import time
import threading
import logging as lg
from logger import init
import shift
from TraderS import TraderS
import sys
from MACD_pipeline import MACD_pipeline
from Volatility_pipeline import Volatility_Pipeline

if __name__=="__main__":
    init()
    lg.debug("App Started")
    try:
        # create trader object
        TraderS.getInstance().sub_all_order_book()
        time.sleep(5)
        # volatility_pipe = Volatility_Pipeline()
        macd_pipe = MACD_pipeline(['CS1', 'CS2'])
        # t1 = threading.Thread(target=volatility_pipe.schedule)
        t2 = threading.Thread(target=macd_pipe.schedule_macd)
        # t1.start()
        t2.start()
        # t1.join()
        t2.join()
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
        TraderS.disconnect()
        lg.debug('Trader connection disconnected Successfully!')
