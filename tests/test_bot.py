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


@pytest.mark.parametrize('data,matches', [
    ({'text': '<@foo>: actors in something', 'type': 'message'}, True),
    ({}, False),
    ({'text': '<@foo>: something else', 'type': 'message'}, False),
    ({'text': 'nothing at all'}, False),
])
def test_message_is_actor_multiple_query(data, matches):
    bot = Halliwell('foo', None, None)
    assert bot.message_is_actor_multiple_query(data) == matches


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


@pytest.mark.parametrize('cast,result', [
    (set(), 'No actors found in bar'),
    ({mock.CoroutineMock()}, 'The following actor is in bar:'),
    (
        {mock.CoroutineMock(), mock.CoroutineMock()},
        'The following actors are in bar:'
    ),
])
@mock.patch('halliwell.bot.movie_finder')
@mock.patch('halliwell.bot.friendly_list')
@pytest.mark.asyncio
async def test_find_overlapping_actors(friendly_list, movie_finder, cast,
                                              result):
    friendly_list.return_value = 'bar'
    mock_first_movie = mock.CoroutineMock(name='One', cast=cast)
    mock_second_movie = mock.CoroutineMock(name='Two', cast=cast)
    first_result_future = asyncio.Future()
    first_result_future.set_result([mock_first_movie])
    second_result_future = asyncio.Future()
    second_result_future.set_result([mock_second_movie])
    movie_finder.find.side_effect = [first_result_future, second_result_future]
    bot = Halliwell('foo', None, None)
    data = {'text': '"foo" "bar"', 'channel': 'channel'}
    response = await bot.find_overlapping_actors(data)
    assert response['text'].startswith(result)
    movie_finder.find.assert_any_call('foo')
    movie_finder.find.assert_any_call('bar')


@mock.patch('halliwell.bot.movie_finder')
@pytest.mark.asyncio
async def test_find_overlapping_actors_no_movie(movie_finder):
    first_result_future = asyncio.Future()
    first_result_future.set_result([])
    movie_finder.find.return_value = first_result_future
    bot = Halliwell('foo', None, None)
    data = {'text': '"foo"', 'channel': 'channel'}
    response = await bot.find_overlapping_actors(data)
    assert response['text'] == "Movie not found: 'foo'"
