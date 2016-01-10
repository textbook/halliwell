import pytest

from halliwell import imdb

from helpers import slow


@slow
@pytest.mark.asyncio
async def test_get_movie_description():
    description = await imdb.get_movie_description('life of brian')
    assert 'The story of Brian of Nazareth' in description


@slow
@pytest.mark.asyncio
async def test_get_person_description():
    description = await imdb.get_person_description('graham chapman')
    assert "Graham's father was a chief police inspector" in description


@slow
@pytest.mark.asyncio
async def test_get_overlapping_movies():
    overlap = await imdb.get_overlapping_movies(
        ['john cleese', 'terry gilliam', 'connie booth']
    )
    assert 'And Now for Something Completely Different' in overlap


@slow
@pytest.mark.asyncio
async def test_get_overlapping_actors():
    overlap = await imdb.get_overlapping_actors([
        'monty python holy grail',
        'meaning of life',
    ])
    assert 'Eric Idle' in overlap
