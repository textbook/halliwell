"""A Slack bot that can give you useful information about movies."""

import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())

__author__ = 'Jonathan Sharpe'
__version__ = '0.7.1'

from .bot import Halliwell
