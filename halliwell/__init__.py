"""A Slack bot that can give you useful information about movies."""

import logging

from .halliwell import Halliwell

logging.getLogger(__name__).addHandler(logging.NullHandler())

__author__ = 'Jonathan Sharpe'
__version__ = '0.0.1'
