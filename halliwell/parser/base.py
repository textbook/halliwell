import abc
from textwrap import dedent


class IMDbBase(metaclass=abc.ABCMeta):

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

    @abc.abstractmethod
    def _data(self):
        """The data to use in :py:method:`__str__`."""
        raise NotImplementedError  # pragma: no cover

    @abc.abstractmethod
    async def update(self):
        """Update the object with additional information."""
        raise NotImplementedError  # pragma: no cover
