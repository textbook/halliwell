"""Functionality for interfacing with the IMDb objects."""
from .parser import person_finder, movie_finder
from .utils import friendly_list


async def get_movie_description(title):
    """Get the description of a movie by title.

    Arguments:
      title (:py:class:`str`): The title of the movie.

    Returns:
      :py:class:`str`: The description of the movie.

    """
    result = await _get_item_description(title, movie_finder)
    return result or 'Movie not found: {!r}'.format(title)


async def get_overlapping_actors(titles):
    movies = []
    movie_titles = []
    for title in titles:
        movie = await _get_item(title, movie_finder)
        if movie is None:
            return 'Movie not found: {!r}'.format(title)
        movies.append(movie)
        movie_titles.append(repr(movie.name))
        await movie.update()
    friendly_titles = friendly_list(movie_titles)
    cast = set.intersection(*[movie.cast for movie in movies])
    if not cast:
        return 'No actors found in {}'.format(friendly_titles)
    if len(cast) == 1:
        template = 'The following actor is in {}:'
    else:
        template = 'The following actors are in {}:'
    return '\n\n'.join([
        template.format(friendly_titles),
    ] + [' - *{0.name}* ({0.url})'.format(actor) for actor in cast])


async def get_person_description(name):
    """Get the description of a person by name.

    Arguments:
      name (:py:class:`str`): The name of the person.

    Returns:
      :py:class:`str`: The description of the person.

    """
    result = await _get_item_description(name, person_finder)
    return result or 'Person not found: {!r}'.format(name)


async def _get_item_description(name, finder):
    item = await _get_item(name, finder)
    if item is not None:
        await item.update()
        return str(item)


async def _get_item(name, inst):
    matches = await inst.find(name)
    if matches:
        return matches[0]
