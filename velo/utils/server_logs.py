"""
Configuration module for http server logs
"""

import logging
from logging import Logger


def logger_server() -> Logger:
    """Format logger, configure file handler and add handler
    for http server logger.

    Returns:
        Logger: Logger for http server
    """

    server_logger = logging.getLogger(__name__)
    server_logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        '%(asctime)s:%(filename)s:%(funcName)s:%(levelname)s:%(message)s:'
    )

    server_file_handler = logging.FileHandler('./logs/server.log')
    server_file_handler.setLevel(logging.DEBUG)
    server_file_handler.setFormatter(formatter)

    server_logger.addHandler(server_file_handler)

    return server_logger


server = logger_server()
