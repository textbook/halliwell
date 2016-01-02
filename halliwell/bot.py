"""An IMDbot built on aSlack and IMDbPY."""

import collections
from textwrap import dedent

from aslack import slack_bot

from . import __author__, __name__ as mod_name, __version__
from .parser import movie_finder


class Halliwell(slack_bot.SlackBot):
    """A bot to look up information on people in the movies."""

    INSTRUCTIONS = dedent("""
    Hello, I am an aSlack bot running on Cloud Foundry ({name} v{version}).

    For more information, see {aslack_url} or contact {author}.
    """.format(
        aslack_url='https://pythonhosted.org/aslack',
        author=__author__,
        name=mod_name,
        version=__version__,
    ))

    def message_is_movie_query(self, data):
        """If you send me a message starting with the word 'movie'"""
        return (self.message_is_to_me(data) and
                data['text'][len(self.address_as):].startswith('movie'))

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

    MESSAGE_FILTERS = collections.OrderedDict([
        (message_is_movie_query, provide_movie_data),
    ])
