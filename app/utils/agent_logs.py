"""
Configuration module for agent logs
"""

import logging
from logging import Logger


def logger_agent() -> Logger:
    """Format logger, configure file handler and add handler
    for agent logger.

    Returns:
        Logger: Logger for agents
    """

    agent_logger = logging.getLogger(__name__)
    agent_logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        '%(asctime)s:%(filename)s:%(funcName)s:%(levelname)s:%(message)s:'
    )

    agent_file_handler = logging.FileHandler('./logs/agents.log')
    agent_file_handler.setLevel(logging.DEBUG)
    agent_file_handler.setFormatter(formatter)

    agent_logger.addHandler(agent_file_handler)

    return agent_logger


agent = logger_agent()
