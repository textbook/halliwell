"""An IMDbot built on aSlack."""

import collections
import logging
from textwrap import dedent

from aslack import slack_bot

from . import __author__, __name__ as mod_name, __version__
from .imdb import (
    get_movie_description,
    get_overlapping_actors,
    get_person_description,
)
from .utils import extract_quoted_text

logger = logging.getLogger(__name__)


class Halliwell(slack_bot.SlackBot):
    """The filmgoer's companion."""

    INSTRUCTIONS = dedent("""
    Hello, I am an aSlack bot running on Cloud Foundry ({name} v{version}).

    For more information, see {url} or contact {author}.
    """.format(
        author=__author__,
        name=mod_name,
        url='https://github.com/textbook/halliwell',
        version=__version__,
    ))

    # Matches

    def message_is_movie_query(self, data):
        """If you send me a message starting with the word 'movie'"""
        return (self.message_is_to_me(data) and
                data['text'][len(self.address_as):].startswith('movie'))

    def message_is_person_query(self, data):
        """If you send me a message starting with the word 'person'"""
        return (self.message_is_to_me(data) and
                data['text'][len(self.address_as):].startswith('person'))

    def message_is_actor_multiple_query(self, data):
        """If you send me a message asking 'actors in' with a quoted list of movies"""
        return (self.message_is_to_me(data) and
                data['text'][len(self.address_as):].startswith('actors in'))

    def message_is_movie_multiple_query(self, data):
        """If you send me a message asking 'movies with' with a quoted list of actors"""
        return (self.message_is_to_me(data) and
                data['text'][len(self.address_as):].startswith('movies with'))

    # Dispatchers

    async def provide_movie_data(self, data):
        """I will tell you about that movie."""
        title = data['text'].split(' ', maxsplit=2)[-1]
        text = await get_movie_description(title)
        return dict(channel=data['channel'], text=text)

    async def provide_person_data(self, data):
        """I will tell you about that person."""
        name = data['text'].split(' ', maxsplit=2)[-1]
        text = await get_person_description(name)
        return dict(channel=data['channel'], text=text)

    async def find_overlapping_actors(self, data):
        """I will find actors appearing in all of those movies."""
        titles = extract_quoted_text(data['text'])
        text = await get_overlapping_actors(titles)
        return dict(channel=data['channel'], text=text)

    MESSAGE_FILTERS = collections.OrderedDict([
        (message_is_movie_query, provide_movie_data),
        (message_is_person_query, provide_person_data),
        (message_is_actor_multiple_query, find_overlapping_actors),
    ])
