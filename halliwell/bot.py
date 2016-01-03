"""An IMDbot built on aSlack and IMDbPY."""

import collections
import logging
from textwrap import dedent

from aslack import slack_bot

from . import __author__, __name__ as mod_name, __version__
from .parser import movie_finder, person_finder

logger = logging.getLogger(__name__)


class Halliwell(slack_bot.SlackBot):
    """A bot to look up information on people in the movies."""

    INSTRUCTIONS = dedent("""
    Hello, I am an aSlack bot running on Cloud Foundry ({name} v{version}).

    For more information, see {aslack_url} or contact {author}.
    """.format(
        aslack_url='https://github.com/textbook/halliwell',
        author=__author__,
        name=mod_name,
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

    # Dispatchers

    async def provide_movie_data(self, data):
        """I will tell you about that movie."""
        title = data['text'].split(' ', maxsplit=2)[-1]
        matches = await movie_finder.find(title)
        if not matches:
            return dict(
                channel=data['channel'],
                text='Movie not found: {!r}'.format(title),
            )
        movie = matches[0]
        await movie.update()
        return dict(channel=data['channel'], text=str(movie))

    async def provide_person_data(self, data):
        """I will tell you about that person."""
        name = data['text'].split(' ', maxsplit=2)[-1]
        matches = await person_finder.find(name)
        if not matches:
            return dict(
                channel=data['channel'],
                text='Person not found: {!r}'.format(name),
            )
        person = matches[0]
        await person.update()
        return dict(channel=data['channel'], text=str(person))

    MESSAGE_FILTERS = collections.OrderedDict([
        (message_is_movie_query, provide_movie_data),
        (message_is_person_query, provide_person_data),
    ])
