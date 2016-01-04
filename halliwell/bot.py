"""An IMDbot built on aSlack and IMDbPY."""

import collections
import logging
from textwrap import dedent

from aslack import slack_bot

from . import __author__, __name__ as mod_name, __version__
from .parser import movie_finder, person_finder
from .utils import extract_quoted_text, friendly_list

logger = logging.getLogger(__name__)


class Halliwell(slack_bot.SlackBot):
    """The filmgoer's companion."""

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

    def message_is_actor_multiple_query(self, data):
        """If you send me a message asking 'actor in' with a quoted list of movies"""
        return (self.message_is_to_me(data) and
                data['text'][len(self.address_as):].startswith('actor in'))

    # Dispatchers

    async def provide_movie_data(self, data):
        """I will tell you about that movie."""
        title = data['text'].split(' ', maxsplit=2)[-1]
        movie = await self._get_item(title, movie_finder)
        if movie is None:
            return dict(
                channel=data['channel'],
                text='Movie not found: {!r}'.format(title),
            )
        await movie.update()
        return dict(channel=data['channel'], text=str(movie))

    async def provide_person_data(self, data):
        """I will tell you about that person."""
        name = data['text'].split(' ', maxsplit=2)[-1]
        person = await self._get_item(name, person_finder)
        if person is None:
            return dict(
                channel=data['channel'],
                text='Person not found: {!r}'.format(name),
            )
        await person.update()
        return dict(channel=data['channel'], text=str(person))

    async def find_overlapping_actors(self, data):
        """I will find actors appearing in all of those movies."""
        movies = []
        movie_titles = []
        for title in extract_quoted_text(data['text']):
            movie = await self._get_item(title, movie_finder)
            if movie is None:
                return dict(
                    channel=data['channel'],
                    text='Movie not found: {!r}'.format(title),
                )
            movies.append(movie)
            movie_titles.append(movie.name)
            await movie.update()
        friendly_titles = friendly_list(movie_titles)
        cast = movies[0].cast
        for movie in movies[1:]:
            cast.intersection_update(movie.cast)
        if not cast:
            return dict(
                channel=data['channel'],
                text='No actors found in {}'.format(friendly_titles),
            )
        text = '\n\n'.join([
            'The following actors are in {}:'.format(friendly_titles),
        ] + [' - *{0.name}* ({0.url})'.format(actor) for actor in cast])
        return dict(channel=data['channel'], text=text)

    @staticmethod
    async def _get_item(name, inst):
        matches = await inst.find(name)
        if matches:
            return matches[0]

    MESSAGE_FILTERS = collections.OrderedDict([
        (message_is_movie_query, provide_movie_data),
        (message_is_person_query, provide_person_data),
        (message_is_actor_multiple_query, find_overlapping_actors),
    ])
