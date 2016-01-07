import asyncio

from asynctest import mock
import pytest

from halliwell.imdb import (
    get_person_description,
    get_overlapping_actors,
    get_movie_description,
)

FIRST_MOCK = mock.CoroutineMock()
SECOND_MOCK = mock.CoroutineMock()


@pytest.mark.parametrize('found,expected', [
    ([], "Movie not found: 'foo'"),
    ([FIRST_MOCK], str(FIRST_MOCK)),
])
@mock.patch('halliwell.imdb.movie_finder')
@pytest.mark.asyncio
async def test_get_movie_description(movie_finder, found, expected):
    result_future = asyncio.Future()
    result_future.set_result(found)
    movie_finder.find.return_value = result_future
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
@mock.patch('halliwell.imdb.movie_finder')
@pytest.mark.asyncio
async def test_get_overlapping_actors(movie_finder, found, expected):
    futures = [asyncio.Future() for _ in found]
    for future, result in zip(futures, found):
        future_result = []
        for details in result:
            mock_movie = mock.CoroutineMock()
            mock_movie.configure_mock(**details)
            future_result.append(mock_movie)
        future.set_result(future_result)
    movie_finder.find.side_effect = futures
    result = await get_overlapping_actors(['foo', 'bar'])
    assert result.startswith(expected)
    movie_finder.find.assert_any_call('foo')
    if found[0]:
        movie_finder.find.assert_any_call('bar')


@pytest.mark.parametrize('found,expected', [
    ([], "Person not found: 'foo'"),
    ([FIRST_MOCK], str(FIRST_MOCK)),
])
@mock.patch('halliwell.imdb.person_finder')
@pytest.mark.asyncio
async def test_get_person_description(person_finder, found, expected):
    result_future = asyncio.Future()
    result_future.set_result(found)
    person_finder.find.return_value = result_future
    assert await get_person_description('foo') == expected
    person_finder.find.assert_called_once_with('foo')
