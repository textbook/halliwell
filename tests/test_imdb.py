import asyncio

from asynctest import mock
import pytest

from halliwell.imdb import (
    get_person_description,
    get_overlapping_actors,
    get_overlapping_movies,
    get_movie_description,
)

from helpers import future_from

FIRST_MOCK = mock.CoroutineMock()
SECOND_MOCK = mock.CoroutineMock()


@pytest.mark.parametrize('found,expected', [
    ([], "Movie not found: 'foo'"),
    ([FIRST_MOCK], str(FIRST_MOCK)),
])
@mock.patch('halliwell.imdb.MOVIE_FINDER')
@pytest.mark.asyncio
async def test_get_movie_description(movie_finder, found, expected):
    movie_finder.find.return_value = future_from(found)
    assert await get_movie_description('foo') == expected
    movie_finder.find.assert_called_once_with('foo')


@pytest.mark.parametrize('found,expected', [
    ([[]], "Movie not found: 'foo'"),
    ([[mock.CoroutineMock()], []], "Movie not found: 'bar'"),
    (
        [[dict(name='foo', cast=set())], [dict(name='bar', cast=set())]],
        "No actors found in 'foo' and 'bar'",
    ),
    (
        [
            [dict(name='foo', cast={FIRST_MOCK})],
            [dict(name='bar', cast={FIRST_MOCK})],
        ],
        "The following actor is in 'foo' and 'bar':",
    ),
    (
        [
            [dict(name='foo', cast={FIRST_MOCK, SECOND_MOCK})],
            [dict(name='bar', cast={FIRST_MOCK, SECOND_MOCK})],
        ],
        "The following actors are in 'foo' and 'bar':",
    ),
])
@mock.patch('halliwell.imdb.MOVIE_FINDER')
@pytest.mark.asyncio
async def test_get_overlapping_actors(movie_finder, found, expected):
    futures = []
    for result in found:
        future_result = []
        for details in result:
            mock_movie = mock.CoroutineMock()
            mock_movie.configure_mock(**details)
            future_result.append(mock_movie)
        futures.append(future_from(future_result))
    movie_finder.find.side_effect = futures
    result = await get_overlapping_actors(['foo', 'bar'])
    assert result.startswith(expected)
    movie_finder.find.assert_any_call('foo')
    if found[0]:
        movie_finder.find.assert_any_call('bar')


@pytest.mark.parametrize('found,expected', [
    ([[]], "Person not found: 'foo'"),
    ([[mock.CoroutineMock()], []], "Person not found: 'bar'"),
    (
        [
            [dict(name='foo', filmography={'actor': set()})],
            [dict(name='bar', filmography={'actor': set()})]
        ],
        "No movies featuring 'foo' and 'bar'",
    ),
    (
        [
            [dict(name='foo', filmography={'actor': {FIRST_MOCK}})],
            [dict(name='bar', filmography={'actor': {FIRST_MOCK}})],
        ],
        "The following movie features 'foo' and 'bar':",
    ),
    (
        [
            [dict(
                name='foo',
                filmography={'actor': {FIRST_MOCK, SECOND_MOCK}},
            )],
            [dict(
                name='bar',
                filmography={'actor': {FIRST_MOCK, SECOND_MOCK}},
            )],
        ],
        "The following movies feature 'foo' and 'bar':",
    ),
])
@mock.patch('halliwell.imdb.PERSON_FINDER')
@pytest.mark.asyncio
async def test_get_overlapping_movies(person_finder, found, expected):
    futures = []
    for result in found:
        future_result = []
        for details in result:
            mock_actor = mock.CoroutineMock()
            mock_actor.configure_mock(**details)
            future_result.append(mock_actor)
        futures.append(future_from(future_result))
    person_finder.find.side_effect = futures
    result = await get_overlapping_movies(['foo', 'bar'])
    assert result.startswith(expected)
    person_finder.find.assert_any_call('foo')
    if found[0]:
        person_finder.find.assert_any_call('bar')


@pytest.mark.parametrize('found,expected', [
    ([], "Person not found: 'foo'"),
    ([FIRST_MOCK], str(FIRST_MOCK)),
])
@mock.patch('halliwell.imdb.PERSON_FINDER')
@pytest.mark.asyncio
async def test_get_person_description(person_finder, found, expected):
    person_finder.find.return_value = future_from(found)
    assert await get_person_description('foo') == expected
    person_finder.find.assert_called_once_with('foo')
