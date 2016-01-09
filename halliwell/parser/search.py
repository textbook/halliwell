"""Search for things on IMDb.

Attributes:
  movie_finder (:py:class:`MovieFinder`): Find movies on IMDb.
  person_finder (:py:class:`PersonFinder`): Find people on IMDb.

"""

import logging
from urllib.parse import quote

import aiohttp
from bs4 import BeautifulSoup, SoupStrainer

from .models import Movie, Person

logger = logging.getLogger(__name__)


class IMDbFinder:
    """Base class for searching IMDb.

    Arguments:
      key (:py:class:`str`): The key for the class of object.
      result_class (:py:class:`IMDbBase`): The type of result to create.

    Attributes:
      SEARCH_URL (:py:class:`str`): The search URL.
      TARGET (:py:class:`bs4.SoupStrainer`): Defines the table
        containing the search results.

    """

    SEARCH_URL = 'http://akas.imdb.com/find?q={query}&s={key}'

    TARGET = SoupStrainer('table', **{'class': 'findList'})

    def __init__(self, key, result_class):
        self.key = key
        self.result_class = result_class

    async def find(self, query, results=10):
        """Find the required content on IMDb.

        Arguments:
          query (:py:class:`str`): The query to search for.
          results (:py:class:`int`, optional): The number of results
            to return (defaults to ``10``).

        Returns:
          :py:class:`list`: A list of :py:attr:`result_class`
            instances containing the search results.

        """
        if results > 200:
            raise ValueError('IMDb only shows up to 200 results')
        url = self.SEARCH_URL.format(key=self.key, query=quote(query, safe=''))
        logger.info('Querying URL {!r}'.format(url))
        response = await aiohttp.get(url)
        logger.debug('Response status: {!r}'.format(response.status))
        if response.status != 200:
            return []
        body = await response.read()
        soup = BeautifulSoup(body, 'html.parser', parse_only=self.TARGET)
        return [self.parse(element) for _, element in
                zip(range(results), soup.findAll('tr'))]

    def parse(self, element):
        """

        Arguments:
          element (:py:class:`bs4.PageElement`): The element to parse.

        Return:
          :py:attr:`IMDbBase`: The object parsed from the element.

        """
        link = element.find('td', attrs={'class': 'result_text'}).find('a')
        return self.result_class.from_link(link)


class MovieFinder(IMDbFinder):
    """Finder specifically for movies.

    Note:
      Adds the ttype to narrow down results to films only.

    """

    SEARCH_URL = 'http://akas.imdb.com/find?q={query}&s={key}&ttype=ft'

    def __init__(self):
        super().__init__('tt', Movie)


movie_finder = MovieFinder()

person_finder = IMDbFinder('nm', Person)
