"""Functionality for interfacing with the IMDb objects."""
from .parser import PERSON_FINDER, MOVIE_FINDER
from .utils import friendly_list


async def get_movie_description(title):
    """Get the description of a movie by title.

    Arguments:
      title (:py:class:`str`): The title of the movie.

    Returns:
      :py:class:`str`: The description of the movie.

    """
    result = await _get_item_description(title, MOVIE_FINDER)
    return result or 'Movie not found: {!r}'.format(title)


async def get_overlapping_actors(titles):
    """Find the actors appearing in multiple movies together.

    Arguments:
      titles (:py:class:`list`): The titles of the movies.

    Returns:
      :py:class:`str`: A description of the actors appearing in all
        specified movies.

    """
    movies = []
    movie_titles = []
    for title in titles:
        movie = await _get_item(title, MOVIE_FINDER)
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
    ] + [
        ' - *{0.name}* ({0.url})'.format(actor) for actor in cast
    ])


async def get_overlapping_movies(names):
    """Find the movies multiple actors have appeared in together.

    Arguments:
      names (:py:class:`list`): The names of the actors.

    Returns:
      :py:class:`str`: A description of the movies featuring all
        specified actors.

    """
    actors = []
    actor_names = []
    for name in names:
        actor = await _get_item(name, PERSON_FINDER)
        if actor is None:
            return 'Person not found: {!r}'.format(name)
        actors.append(actor)
        actor_names.append(repr(actor.name))
        await actor.update()
    friendly_names = friendly_list(actor_names)
    movies = set.intersection(*[actor.filmography['actor'] for actor in actors])
    if not movies:
        return 'No movies featuring {} found'.format(friendly_names)
    if len(movies) == 1:
        template = 'The following movie features {}:'
    else:
        template = 'The following movies feature {}:'
    return '\n\n'.join([
        template.format(friendly_names)
    ] + [
        ' - *{0.name}* ({0.url})'.format(movie) for movie in movies
    ])


async def get_person_description(name):
    """Get the description of a person by name.

    Arguments:
      name (:py:class:`str`): The name of the person.

    Returns:
      :py:class:`str`: The description of the person.

    """
    result = await _get_item_description(name, PERSON_FINDER)
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
