import abc
import logging
import re
from collections import defaultdict
from html import escape
from textwrap import dedent

import aiohttp
from aslack.utils import truncate
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class IMDbBase(metaclass=abc.ABCMeta):
    """Base class for IMDb objects.

    Arguments:
      id_ (:py:class:`str`): The IMDb ID of the object.
      name (:py:class:`str`): The name of the object.

    Attributes:
      BASE_URL (:py:class:`str`): The base URL for IMDb access.
      FRIENDLY_URL (:py:class:`str`): The format for the user-friendly
        URL.
      URL_REGEX (:py:class:`SRE_Pattern`): The regular expression
        matching URLs of the current type of object.

    """

    BASE_URL = 'http://akas.imdb.com'

    FRIENDLY_URL = None

    URL_REGEX = None

    def __init__(self, id_, name):
        self.id_ = id_
        self.name = name
        self.url = self.FRIENDLY_URL.format(id_=id_)

    def __eq__(self, other):
        try:
            return self.id_ == other.id_
        except AttributeError:
            return False

    def __hash__(self):
        return hash(self.id_)

    def __str__(self):
        return dedent("""
        *{name}*

        {data}

        For more information see: {url}
        """).format(name=self.name, data=self._data(), url=self.url).strip()

    @classmethod
    def from_link(cls, link):
        id_ = cls.URL_REGEX.match(link['href']).group(1)
        return cls(id_, link.string)

    @classmethod
    async def from_id(cls, type_, id_):
        response = await aiohttp.get('/'.join((cls.BASE_URL, type_, id_)))
        if response.status != 200:
            raise ValueError("Nothing found at '/{}/{}'".format(type_, id_))
        body = await response.read()
        soup = BeautifulSoup(body, 'html.parser')
        title = soup.select('h1 > span[itemprop=name]')[0].string.strip()
        return cls(id_, title)

    @abc.abstractmethod
    def _data(self):
        """The data to use in :py:method:`__str__`."""
        raise NotImplementedError  # pragma: no cover

    @abc.abstractmethod
    async def update(self):
        """Update the object with additional information."""
        raise NotImplementedError  # pragma: no cover


class Movie(IMDbBase):
    """Represents a movie on IMDb.

    Attributes:
      COMBINED_URL (:py:class:`str`): The URL to extract combined data
        from.
      DEFAULT_PLOT (:py:class:`str`): The default plot to show if none
        is available.
      PLOT_URL (:py:class:`str`): The URL to extract plot data from.

    """

    COMBINED_URL = 'http://akas.imdb.com/title/{id_}/combined'

    DEFAULT_PLOT = escape('<no plot summary found>')

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


class Person(IMDbBase):
    """Represents a person on IMDb.

    Attributes:
      BIO_URL (:py:class:`str`): The URL to extract biographical data
        from.
      DEFAULT_BIO (:py:class:`str`): The default biography to show if
        none is available.
      DETAILS_URL (:py:class:`str`): The URL to extract detailed
        information from.

    """

    BIO_URL = 'http://akas.imdb.com/name/{id_}/bio'

    DEFAULT_BIO = escape('<no biographical information found>')

    DETAILS_URL = 'http://akas.imdb.com/name/{id_}/maindetails'

    FRIENDLY_URL = 'http://www.imdb.com/name/{id_}/'

    URL_REGEX = re.compile(r'^/name/(nm\d{7})')

    def __init__(self, id_, name):
        super().__init__(id_, name)
        self.bio = None
        self.filmography = None

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

    async def get_filmography(self):
        """Parses filmography information from IMDb.

        Returns:
          :py:class:`dict`: The person's filmography, as a mapping
            from credit type (:py:class:`str`, e.g. ``'actor'``) to
            a py:class:`set` of :py:class:`Movie` objects.

        """
        url = self.DETAILS_URL.format(id_=self.id_)
        logger.info('Querying URL {!r}'.format(url))
        response = await aiohttp.get(url)
        logger.debug('Response status: {!r}'.format(response.status))
        if response.status != 200:
            return {}
        body = await response.read()
        filmography = defaultdict(set)
        soup = BeautifulSoup(body, 'html.parser')
        roles = soup.select('#filmography > div.head')
        credits = soup.select('#filmography > div.filmo-category-section')
        for role, films in zip(roles, credits):
            role_name = role['data-category']
            role_name = 'actor' if role_name == 'actress' else role_name
            for link in films.select('div > b > a'):
                filmography[role_name].add(Movie.from_link(link))
        return filmography

    async def update(self):
        """Update the person with additional information."""
        if self.bio is None:
            bio = await self.get_bio()
            if bio is None:
                self.bio = self.DEFAULT_BIO
            else:
                self.bio = truncate(bio.strip())
        if self.filmography is None:
            self.filmography = await self.get_filmography()

    def _data(self):
        """The data to use in :py:method:`__str__`."""
        return self.bio
