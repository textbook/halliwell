"""Utility functions used by the IMDb functionality."""

import logging

import aiohttp

logger = logging.getLogger(__name__)


async def get_page_content(url):
    """Get the content of a web page.

    Arguments:
      url (:py:class:`str`): The URL to access.

    Returns:
      :py:class:`str`: The page content.

    """
    logger.info('Querying URL %r', url)
    response = await aiohttp.get(url)
    logger.debug('Response status: %r', response.status)
    if response.status == 200:
        return await response.read()
