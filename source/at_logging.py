import logging
import os

def setup_custom_logger(name):
    logFormatter    = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s :: %(message)s', "%H:%M:%S")
    rootLogger      = logging.getLogger(name)
    consoleHandler  = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)
    rootLogger.setLevel(logging.DEBUG)
    return rootLogger

def addLoggingToFile(loggerName, logPath, logFileName):
    rootLogger = logging.getLogger(loggerName)

    fileHandler = logging.FileHandler(os.path.join(logPath, logFileName))
    logFormatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(message)s', "%H:%M:%S")

    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)
