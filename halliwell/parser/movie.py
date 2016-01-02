"""Functionality for handling IMDb movies."""

import logging
from textwrap import dedent

import aiohttp
from aslack.utils import truncate
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class Movie:
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

    DEFAULT_PLOT = '&lt;no plot summary found&gt;'

    FRIENDLY_URL = 'http://www.imdb.com/title/{id_}/'

    PLOT_URL = 'http://akas.imdb.com/title/{id_}/plotsummary'

    def __init__(self, id_, name):
        self.id_ = id_
        self.name = name
        self.url = self.FRIENDLY_URL.format(id_=id_)
        self.plot = None

    def __str__(self):
        return dedent("""
        *{name}*

        {plot}

        For more information see: {url}
        """).format(name=self.name, plot=self.plot, url=self.url).strip()

    async def update(self):
        plot = await self.get_plot()
        self.plot = truncate(plot) if plot is not None else self.DEFAULT_PLOT

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
