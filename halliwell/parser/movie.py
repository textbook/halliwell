"""Functionality for handling IMDb movies."""

import logging
import re

import aiohttp
from aslack.utils import truncate
from bs4 import BeautifulSoup

from .base import IMDbBase
from .person import Person

logger = logging.getLogger(__name__)


class Movie(IMDbBase):
    """Represents a movie on IMDb.

    Arguments:
      id_ (:py:class:`str`): The IMDb ID of the movie.
      name (:py:class:`str`): The name of the movie.

    Attributes:
      DEFAULT_PLOT (:py:class:`str`): The default plot to show if none
        is available.
      FRIENDLY_URL (:py:class:`str`): The format for the user-friendly
        URL.
      PLOT_URL (:py:class:`str`): The URL to extract plot data from.

    """

    COMBINED_URL = 'http://akas.imdb.com/title/{id_}/combined'

    DEFAULT_PLOT = '&lt;no plot summary found&gt;'

    FRIENDLY_URL = 'http://www.imdb.com/title/{id_}/'

    PLOT_URL = 'http://akas.imdb.com/title/{id_}/plotsummary'

    URL_REGEX = re.compile(r'^/title/(tt\d{7})')

    def __init__(self, id_, name):
        super().__init__(id_, name)
        self.cast = None
        self.plot = None

    async def get_cast(self):
        """Parse cast information from IMDb.

        Returns:
          :py:class:`set`: A set of :py:class:`Person` objects.

        """
        url = self.COMBINED_URL.format(id_=self.id_)
        logger.info('Querying URL {!r}'.format(url))
        response = await aiohttp.get(url)
        logger.debug('Response status: {!r}'.format(response.status))
        if response.status != 200:
            return set()
        body = await response.read()
        soup = BeautifulSoup(body, 'html.parser')
        cast_list = soup.find('table', attrs={'class', 'cast'})
        cast = set()
        if cast_list is None:
            return cast
        for element in cast_list.findAll('tr'):
            classes = element.attrs.get('class', [])
            if 'odd' not in classes and 'even' not in classes:
                continue
            link = element.find('td', attrs={'class': 'nm'}).find('a')
            cast.add(Person.from_link(link))
        return cast

    async def get_plot(self):
        """Parse plot information from IMDb.

        Note:
          If there are plot summaries, returns the first one.
          Otherwise, returns the plot synopsis. If neither is present,
          returns ``None``.

        Returns:
          :py:class:`str`: A summary of the movie's plot.

        """
        url = self.PLOT_URL.format(id_=self.id_)
        logger.info('Querying URL {!r}'.format(url))
        response = await aiohttp.get(url)
        logger.debug('Response status: {!r}'.format(response.status))
        if response.status != 200:
            return
        body = await response.read()
        soup = BeautifulSoup(body, 'html.parser')
        summary_list = soup.find('ul', attrs={'class', 'zebraList'})
        if summary_list is not None:
            summaries = summary_list.find_all('li')
            if summaries:
                return summaries[0].find(
                    'p', attrs={'class': 'plotSummary'},
                ).string
        synopsis = soup.find('div', attrs={'id': 'plotSynopsis'})
        if synopsis is not None:
            return synopsis.string

    async def update(self):
        """Update the movie with additional information."""
        if self.plot is None:
            plot = await self.get_plot()
            if plot is None:
                self.plot = self.DEFAULT_PLOT
            else:
                self.plot = truncate(plot.strip())
        if self.cast is None:
            self.cast = await self.get_cast()

    def _data(self):
        """The data to use in :py:method:`__str__`."""
        return self.plot
