import logging as lg
format = "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  [%(filename)s] [%(funcName)s] :: %(message)s"
lg.basicConfig(format=format, level=lg.DEBUG)
logFormatter = lg.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  [%(filename)s] [%(funcName)s] :: %(message)s")
rootLogger = lg.getLogger()

fileHandler = lg.FileHandler("{0}.log".format('seeking_alpha'))
fileHandler.setFormatter(logFormatter)
fileHandler.setLevel(lg.DEBUG)
rootLogger.addHandler(fileHandler)

consoleHandler = lg.StreamHandler()
consoleHandler.setFormatter(logFormatter)
consoleHandler.setLevel(lg.DEBUG)
#rootLogger.addHandler(consoleHandler)