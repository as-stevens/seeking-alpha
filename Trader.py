import shift
from credentials import my_password, my_username
class Trader:

    __instance = None

    @staticmethod
    def getInstance():
      """ Static access method. """
      if Trader.__instance == None:
         Trader()
      return Trader.__instance

    def __init__(self):
      """ Virtually private constructor. """
      if Trader.__instance != None:
         raise Exception("This class is a singleton!")
      else:
           try:
               # create trader object
               trader = shift.Trader(my_username)
               # connection & subs to order_book
               trader.connect("initiator.cfg", my_password)
               Trader.__instance = trader
           except shift.IncorrectPasswordError as e:
               print(e)
           except shift.ConnectionTimeoutError as e:
               print(e)


    def disconnect(self):
      Trader.__instance().disconnect()
      print('Trader connection disconnected')