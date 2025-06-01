from sys import stdout
from logging import (
    getLogger
    ,Formatter
    ,StreamHandler
    ,FileHandler
    ,INFO
)

# get logger
logger = getLogger()

# create formatter
formatter = Formatter(
    fmt='request: %(message)s'
)

# create handlers
streamHandler = StreamHandler(stream=stdout)
# fileHandler = FileHandler('app.log')

# create formatters
streamHandler.setFormatter(fmt=formatter)
# fileHandler.setFormatter(fmt=formatter)

# add hanlers to the logger
logger.handlers = [
    streamHandler
    # ,fileHandler
]

# set log-level
logger.setLevel(level=INFO)