"""An IMDbot built on aSlack and IMDbPY."""

from textwrap import dedent

from aslack import __author__, slack_bot


class Halliwell(slack_bot.SlackBot):
    """A bot to look up information on people in the movies."""

    INSTRUCTIONS = dedent("""
    Hello, I am an aSlack bot running on Cloud Foundry.

    For more information, see {aslack_url} or contact {author}.
    """.format(
        aslack_url='https://pythonhosted.org/aslack',
        author=__author__,
    ))
