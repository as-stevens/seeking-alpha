import shift
from credentials import my_password, my_username
class TraderS:

    __instance = None

    @staticmethod
    def getInstance():
      """ Static access method. """
      if TraderS.__instance == None:
         TraderS()
      return TraderS.__instance

    def __init__(self):
      """ Virtually private constructor. """
      if TraderS.__instance != None:
         raise Exception("This class is a singleton!")
      else:
           try:
               # create trader object
               trader = shift.Trader(my_username)
               # connection & subs to order_book
               trader.connect("initiator.cfg", my_password)
               TraderS.__instance = trader
           except shift.IncorrectPasswordError as e:
               print(e)
           except shift.ConnectionTimeoutError as e:
               print(e)

    @staticmethod
    def disconnect():
      TraderS.getInstance().disconnect()
      print('Trader connection disconnected')