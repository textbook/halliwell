"""Generic utility functions.

Attributes:
  QUOTED_MATCHER (:py:class:`SRE_Pattern`): The regex pattern for
    matching quoted text.

"""

import re

QUOTED_MATCHER = re.compile(r'"([^"]+)"')


def extract_quoted_text(text):
    """Extract quoted portions of the supplied text.

    Arguments:
      text (:py:class:`str`): The text to extract from.

    Returns:
      :py:class:`list`: List of regex matches.

    """
    return QUOTED_MATCHER.findall(text)


def friendly_list(string_list):
    """Friendly formatting of a list of strings.

    Arguments:
      string_list (:py:class:`list`): List of strings to format.

    Returns:
      :py:class:`str`: The friendly format.

    """
    if len(string_list) < 2:
        return ''.join(string_list)
    elif len(string_list) == 2:
        return ' and '.join(string_list)
    return ', '.join(string_list[:-2]) + ', ' + ' and '.join(string_list[-2:])
