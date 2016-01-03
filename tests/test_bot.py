import asyncio

import pytest
from asynctest import mock

from halliwell import Halliwell


@pytest.mark.parametrize('data,matches', [
    ({'text': '<@foo>: person something', 'type': 'message'}, True),
    ({}, False),
    ({'text': '<@foo>: something else', 'type': 'message'}, False),
    ({'text': 'nothing at all'}, False),
])
def test_message_is_person_query(data, matches):
    bot = Halliwell('foo', None, None)
    assert bot.message_is_person_query(data) == matches


@pytest.mark.parametrize('data,matches', [
    ({'text': '<@foo>: movie something', 'type': 'message'}, True),
    ({}, False),
    ({'text': '<@foo>: something else', 'type': 'message'}, False),
    ({'text': 'nothing at all'}, False),
])
def test_message_is_movie_query(data, matches):
    bot = Halliwell('foo', None, None)
    assert bot.message_is_movie_query(data) == matches


@mock.patch('halliwell.bot.movie_finder')
@pytest.mark.asyncio
async def test_provide_movie_data_missing(movie_finder):
    result_future = asyncio.Future()
    result_future.set_result([])
    movie_finder.find.return_value = result_future
    bot = Halliwell('foo', None, None)
    data = {'text': 'foo bar baz etc', 'channel': 'channel'}
    expected = {'channel': 'channel', 'text': "Movie not found: 'baz etc'"}
    assert await bot.provide_movie_data(data) == expected
    movie_finder.find.assert_called_once_with('baz etc')


@mock.patch('halliwell.bot.movie_finder')
@pytest.mark.asyncio
async def test_provide_movie_data(movie_finder):
    mock_movie = mock.CoroutineMock()
    result_future = asyncio.Future()
    result_future.set_result([mock_movie])
    movie_finder.find.return_value = result_future
    bot = Halliwell('foo', None, None)
    data = {'text': 'foo bar baz etc', 'channel': 'channel'}
    expected = {'channel': 'channel', 'text': str(mock_movie)}
    assert await bot.provide_movie_data(data) == expected
    movie_finder.find.assert_called_once_with('baz etc')


@mock.patch('halliwell.bot.person_finder')
@pytest.mark.asyncio
async def test_provide_person_data_missing(person_finder):
    result_future = asyncio.Future()
    result_future.set_result([])
    person_finder.find.return_value = result_future
    bot = Halliwell('foo', None, None)
    data = {'text': 'foo bar baz etc', 'channel': 'channel'}
    expected = {'channel': 'channel', 'text': "Person not found: 'baz etc'"}
    assert await bot.provide_person_data(data) == expected
    person_finder.find.assert_called_once_with('baz etc')


@mock.patch('halliwell.bot.person_finder')
@pytest.mark.asyncio
async def test_provide_person_data(person_finder):
    mock_person = mock.CoroutineMock()
    result_future = asyncio.Future()
    result_future.set_result([mock_person])
    person_finder.find.return_value = result_future
    bot = Halliwell('foo', None, None)
    data = {'text': 'foo bar baz etc', 'channel': 'channel'}
    expected = {'channel': 'channel', 'text': str(mock_person)}
    assert await bot.provide_person_data(data) == expected
    person_finder.find.assert_called_once_with('baz etc')
