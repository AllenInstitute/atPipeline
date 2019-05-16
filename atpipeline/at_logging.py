import logging
import os
import types

def log_newline(self, how_many_lines=1):
    # Switch handler, output a blank line
    self.removeHandler(self.console_handler)
    self.addHandler(self.blank_handler)
    for i in range(how_many_lines):
        self.info('')

    # Switch back
    self.removeHandler(self.blank_handler)
    self.addHandler(self.console_handler)

def create_logger(name):

    #Create log handlers
    console_handler  = logging.StreamHandler()
    log_formatter    = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s :: %(message)s', "%H:%M:%S")
    console_handler.setFormatter(log_formatter)

    logger          = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)

    # Create a "blank line" handler
    blank_formatter = logging.Formatter(fmt="")
    blank_handler = logging.StreamHandler()
    blank_handler.setLevel(logging.DEBUG)
    blank_handler.setFormatter(logging.Formatter(fmt=''))

    # Save some data and add a method to logger object
    logger.console_handler = console_handler
    logger.blank_handler = blank_handler
    logger.newline = types.MethodType(log_newline, logger)

    return logger

def add_logging_to_file(logger_name, logfilename):
    logger = logging.getLogger(logger_name)

    fileHandler = logging.FileHandler(logfilename)
    logFormatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(message)s', "%H:%M:%S")

    fileHandler.setFormatter(logFormatter)
    logger.addHandler(fileHandler)
