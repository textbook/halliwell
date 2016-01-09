import asyncio
from textwrap import dedent

from asynctest import mock
import pytest

from halliwell.parser import Movie, Person

from helpers import future_from


def test_init():
    movie = Movie('foo', 'bar')
    assert movie.id_ == 'foo'
    assert movie.name == 'bar'
    assert movie.plot is None
    assert movie.cast is None


def test_str():
    movie = Movie('foo', 'bar')
    assert str(movie).startswith('*bar*')
    assert str(movie).endswith(
        'For more information see: http://www.imdb.com/title/foo/',
    )


@mock.patch('halliwell.parser.models.aiohttp')
@pytest.mark.asyncio
async def test_find_plot_from_synopsis(aiohttp):
    html = dedent("""
    <body>
        <div id="plotSynopsis">Hello</div>
    </body>
    """)
    resp_future = future_from(mock.MagicMock(
        status=200,
        **{'read.return_value': future_from(html)}
    ))
    aiohttp.get.return_value = resp_future
    movie = Movie('foo', None)
    assert await movie.get_plot() == 'Hello'
    aiohttp.get.assert_called_once_with(
        'http://akas.imdb.com/title/foo/plotsummary',
    )


@mock.patch('halliwell.parser.models.aiohttp')
@pytest.mark.asyncio
async def test_find_plot_from_summaries(aiohttp):
    html = dedent("""
    <body>
        <ul class="zebraList">
            <div class="header">Who cares</div>
            <li class="odd"><p class="plotSummary">Hello</p></li>
            <li class="even"><p class="plotSummary">World</p></li>
        </ul>
    </body>
    """)
    resp_future = future_from(mock.MagicMock(
        status=200,
        **{'read.return_value': future_from(html)}
    ))
    aiohttp.get.return_value = resp_future
    movie = Movie('foo', None)
    assert await movie.get_plot() == 'Hello'
    aiohttp.get.assert_called_once_with(
        'http://akas.imdb.com/title/foo/plotsummary',
    )


@mock.patch('halliwell.parser.models.aiohttp')
@pytest.mark.asyncio
async def test_find_plot_no_data(aiohttp):
    resp_future = future_from(mock.MagicMock(
        status=200,
        **{'read.return_value': future_from("<body></body>")}
    ))
    aiohttp.get.return_value = resp_future
    movie = Movie('foo', None)
    assert await movie.get_plot() is None
    aiohttp.get.assert_called_once_with(
        'http://akas.imdb.com/title/foo/plotsummary',
    )


@mock.patch('halliwell.parser.models.aiohttp')
@pytest.mark.asyncio
async def test_find_plot_no_response(aiohttp):
    aiohttp.get.return_value = future_from(mock.MagicMock(status=404))
    movie = Movie('foo', None)
    assert await movie.get_plot() is None
    aiohttp.get.assert_called_once_with(
        'http://akas.imdb.com/title/foo/plotsummary',
    )


@mock.patch('halliwell.parser.models.aiohttp')
@pytest.mark.asyncio
async def test_update_no_plot(aiohttp):
    aiohttp.get.return_value = future_from(mock.MagicMock(status=404))
    movie = Movie('foo', None)
    movie.cast = set()
    assert await movie.update() is None
    assert 'no plot summary found' in movie.plot
    aiohttp.get.assert_called_once_with(
        'http://akas.imdb.com/title/foo/plotsummary',
    )


@mock.patch('halliwell.parser.models.aiohttp')
@pytest.mark.asyncio
async def test_update_plot(aiohttp):
    html = dedent("""
    <body>
        <div id="plotSynopsis">Hello</div>
    </body>
    """)
    resp_future = future_from(mock.MagicMock(
        status=200,
        **{'read.return_value': future_from(html)}
    ))
    aiohttp.get.return_value = resp_future
    movie = Movie('foo', None)
    movie.cast = set()
    assert await movie.update() is None
    assert movie.plot == 'Hello'
    aiohttp.get.assert_called_once_with(
        'http://akas.imdb.com/title/foo/plotsummary',
    )


@mock.patch('halliwell.parser.models.aiohttp')
@pytest.mark.asyncio
async def test_find_cast(aiohttp):
    html = dedent("""
    <body>
        <table class="cast"><tbody>
            <tr class="odd">
                <td></td><td class="nm"><a href="/name/nm0123456">Foo</a></td>
            </tr>
            <tr></tr>
            <tr class="even">
                <td></td><td class="nm"><a href="/name/nm1234567">Bar</a></td>
            </tr>
        </tbody></table>
    </body>
    """)
    resp_future = future_from(mock.MagicMock(
        status=200,
        **{'read.return_value': future_from(html)}
    ))
    aiohttp.get.return_value = resp_future
    movie = Movie('foo', None)
    cast = await movie.get_cast()
    assert len(cast) == 2
    assert Person('nm0123456', None) in cast
    assert Person('nm1234567', None) in cast
    aiohttp.get.assert_called_once_with(
        'http://akas.imdb.com/title/foo/combined',
    )


@mock.patch('halliwell.parser.models.aiohttp')
@pytest.mark.asyncio
async def test_find_cast_no_cast(aiohttp):
    resp_future = future_from(mock.MagicMock(
        status=200,
        **{'read.return_value': future_from("<body></body>")}
    ))
    aiohttp.get.return_value = resp_future
    movie = Movie('foo', None)
    cast = await movie.get_cast()
    assert len(cast) == 0
    aiohttp.get.assert_called_once_with(
        'http://akas.imdb.com/title/foo/combined',
    )


@mock.patch('halliwell.parser.models.aiohttp')
@pytest.mark.asyncio
async def test_find_cast_no_response(aiohttp):
    aiohttp.get.return_value = future_from(mock.MagicMock(status=404))
    movie = Movie('foo', None)
    assert await movie.get_cast() == set()
    aiohttp.get.assert_called_once_with(
        'http://akas.imdb.com/title/foo/combined',
    )


@mock.patch.object(Movie, 'get_cast')
@pytest.mark.asyncio
async def test_update_cast(get_cast):
    get_cast.return_value = future_from(set())
    movie = Movie('foo', None)
    movie.plot = ''
    await movie.update()
    assert movie.cast == set()
    get_cast.assert_called_once_with()


@mock.patch.object(Movie, 'get_cast')
@pytest.mark.asyncio
async def test_update_cast_exists(get_cast):
    get_cast.return_value = future_from(set())
    movie = Movie('foo', None)
    movie.plot = ''
    movie.cast = set()
    await movie.update()
    assert movie.cast == set()
    get_cast.assert_not_called()
