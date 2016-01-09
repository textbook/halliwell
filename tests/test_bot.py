import asyncio

import pytest
from asynctest import mock

from halliwell import Halliwell

@pytest.fixture
def bot():
    return Halliwell('foo', None, None)


@pytest.mark.parametrize('data,matches', [
    ({'text': '<@foo>: person something', 'type': 'message'}, True),
    ({}, False),
    ({'text': '<@foo>: something else', 'type': 'message'}, False),
    ({'text': 'nothing at all'}, False),
])
def test_message_is_person_query(bot, data, matches):
    assert bot.message_is_person_query(data) == matches


@pytest.mark.parametrize('data,matches', [
    ({'text': '<@foo>: movie something', 'type': 'message'}, True),
    ({}, False),
    ({'text': '<@foo>: something else', 'type': 'message'}, False),
    ({'text': 'nothing at all'}, False),
])
def test_message_is_movie_query(bot, data, matches):
    assert bot.message_is_movie_query(data) == matches


@pytest.mark.parametrize('data,matches', [
    ({'text': '<@foo>: actors in something', 'type': 'message'}, True),
    ({}, False),
    ({'text': '<@foo>: something else', 'type': 'message'}, False),
    ({'text': 'nothing at all'}, False),
])
def test_message_is_actor_multiple_query(bot, data, matches):
    assert bot.message_is_actor_multiple_query(data) == matches


@pytest.mark.parametrize('data,matches', [
    ({'text': '<@foo>: movies with something', 'type': 'message'}, True),
    ({}, False),
    ({'text': '<@foo>: something else', 'type': 'message'}, False),
    ({'text': 'nothing at all'}, False),
])
def test_message_is_movie_multiple_query(bot, data, matches):
    assert bot.message_is_movie_multiple_query(data) == matches


@mock.patch('halliwell.bot.get_movie_description')
@pytest.mark.asyncio
async def test_provide_movie_data(get_movie_description, bot):
    result_future = asyncio.Future()
    result_future.set_result('hello world')
    get_movie_description.return_value = result_future
    data = {'text': 'foo bar baz etc', 'channel': 'channel'}
    expected = {'channel': 'channel', 'text': 'hello world'}
    assert await bot.provide_movie_data(data) == expected
    get_movie_description.assert_called_once_with('baz etc')


@mock.patch('halliwell.bot.get_person_description')
@pytest.mark.asyncio
async def test_provide_person_data(get_person_description, bot):
    result_future = asyncio.Future()
    result_future.set_result('hello world')
    get_person_description.return_value = result_future
    data = {'text': 'foo bar baz etc', 'channel': 'channel'}
    expected = {'channel': 'channel', 'text': 'hello world'}
    assert await bot.provide_person_data(data) == expected
    get_person_description.assert_called_once_with('baz etc')


@mock.patch('halliwell.bot.get_overlapping_actors')
@pytest.mark.asyncio
async def test_find_overlapping_actors(get_overlapping_actors, bot):
    result_future = asyncio.Future()
    result_future.set_result('hello world')
    get_overlapping_actors.return_value = result_future
    data = {'text': '"foo" "bar"', 'channel': 'channel'}
    expected = {'text': 'hello world', 'channel': 'channel'}
    assert await bot.find_overlapping_actors(data) == expected
    get_overlapping_actors.assert_called_once_with(['foo', 'bar'])


@mock.patch('halliwell.bot.get_overlapping_movies')
@pytest.mark.asyncio
async def test_find_overlapping_movies(get_overlapping_movies, bot):
    result_future = asyncio.Future()
    result_future.set_result('hello world')
    get_overlapping_movies.return_value = result_future
    data = {'text': '"foo" "bar"', 'channel': 'channel'}
    expected = {'text': 'hello world', 'channel': 'channel'}
    assert await bot.find_overlapping_movies(data) == expected
    get_overlapping_movies.assert_called_once_with(['foo', 'bar'])
