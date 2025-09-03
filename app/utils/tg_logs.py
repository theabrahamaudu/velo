"""
Configuration module for telegram bot logs
"""

import logging
from logging import Logger


def logger_tg() -> Logger:
    """Format logger, configure file handler and add handler
    for telegram bot.

    Returns:
        Logger: Logger for model server side
    """

    tg_logger = logging.getLogger(__name__)
    tg_logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        '%(asctime)s:%(filename)s:%(funcName)s:%(levelname)s:%(message)s:'
    )

    tg_file_handler = logging.FileHandler('./logs/tg_bot.log')
    tg_file_handler.setLevel(logging.DEBUG)
    tg_file_handler.setFormatter(formatter)

    tg_logger.addHandler(tg_file_handler)

    return tg_logger


tg_bot = logger_tg()
