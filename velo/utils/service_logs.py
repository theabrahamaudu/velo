"""
Configuration module for service logs
"""

import logging
from logging import Logger


def logger_service() -> Logger:
    """Format logger, configure file handler and add handler
    for service logger.

    Returns:
        Logger: Logger for services
    """

    service_logger = logging.getLogger(__name__)
    service_logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        '%(asctime)s:%(filename)s:%(funcName)s:%(levelname)s:%(message)s:'
    )

    service_file_handler = logging.FileHandler('./logs/services.log')
    service_file_handler.setLevel(logging.DEBUG)
    service_file_handler.setFormatter(formatter)

    service_logger.addHandler(service_file_handler)

    return service_logger


service = logger_service()
