"""Functionality for handling IMDb people."""

import logging
import re

import aiohttp
from aslack.utils import truncate
from bs4 import BeautifulSoup

from .base import IMDbBase

logger = logging.getLogger(__name__)


class Person(IMDbBase):
    """Represents a person on IMDb.

    Arguments:
      id_ (:py:class:`str`): The IMDb ID of the person.
      name (:py:class:`str`): The name of the person.

    """

    BIO_URL = 'http://akas.imdb.com/name/{id_}/bio'

    DEFAULT_BIO = '&lt;no biographical information found&gt;'

    FRIENDLY_URL = 'http://www.imdb.com/name/{id_}/'

    URL_REGEX = re.compile(r'^/name/(nm\d{7})')

    def __init__(self, id_, name):
        super().__init__(id_, name)
        self.bio = None

    async def get_bio(self):
        """Parse biographical information from IMDb.

        Returns:
          :py:class:`str`: The person's biography.

        """
        url = self.BIO_URL.format(id_=self.id_)
        logger.info('Querying URL {!r}'.format(url))
        response = await aiohttp.get(url)
        logger.debug('Response status: {!r}'.format(response.status))
        if response.status != 200:
            return
        body = await response.read()
        soup = BeautifulSoup(body, 'html.parser')
        bio_link = soup.find('a', attrs={'name': 'mini_bio'})
        logger.debug(bio_link)
        for sibling in bio_link.next_siblings:
            logger.debug(sibling)
            if sibling.name == 'div':
                return sibling.p.text

    async def update(self):
        """Update the person with additional information."""
        bio = await self.get_bio()
        if bio is None:
            self.bio = self.DEFAULT_BIO
        else:
            self.bio = truncate(bio.strip())

    def _data(self):
        """The data to use in :py:method:`__str__`."""
        return self.bio
