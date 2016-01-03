"""Functionality for handling IMDb people."""

import logging
from textwrap import dedent

import aiohttp
from aslack.utils import truncate
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class Person:
    """Represents a person on IMDb.

    Arguments:
      id_ (:py:class:`str`): The IMDb ID of the person.
      name (:py:class:`str`): The name of the person.

    """

    BIO_URL = 'http://akas.imdb.com/name/{id_}/bio'

    DEFAULT_BIO = '&lt;no biographical information found&gt;'

    FRIENDLY_URL = 'http://www.imdb.com/name/{id_}/'

    def __init__(self, id_, name):
        self.id_ = id_
        self.name = name
        self.bio = None
        self.url = self.FRIENDLY_URL.format(id_=id_)

    def __str__(self):
        return dedent("""
        *{name}*

        {bio}

        For more information see: {url}
        """).format(name=self.name, bio=self.bio, url=self.url).strip()

    async def update(self):
        """Update the person with additional information."""
        bio = await self.get_bio()
        if bio is None:
            self.bio = self.DEFAULT_BIO
        else:
            self.bio = truncate(bio.strip())

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
