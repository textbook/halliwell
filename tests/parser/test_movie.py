import asyncio
from textwrap import dedent

from asynctest import mock
import pytest

from halliwell.parser.movie import Movie
from halliwell.parser.person import Person


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


@mock.patch('halliwell.parser.movie.aiohttp')
@pytest.mark.asyncio
async def test_find_plot_from_synopsis(aiohttp):
    html = dedent("""
    <body>
        <div id="plotSynopsis">Hello</div>
    </body>
    """)
    html_future = asyncio.Future()
    html_future.set_result(html)
    resp_future = asyncio.Future()
    resp_future.set_result(mock.MagicMock(
        status=200,
        **{'read.return_value': html_future}
    ))
    aiohttp.get.return_value = resp_future
    movie = Movie('foo', None)
    assert await movie.get_plot() == 'Hello'
    aiohttp.get.assert_called_once_with(
        'http://akas.imdb.com/title/foo/plotsummary',
    )


@mock.patch('halliwell.parser.movie.aiohttp')
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
    html_future = asyncio.Future()
    html_future.set_result(html)
    resp_future = asyncio.Future()
    resp_future.set_result(mock.MagicMock(
        status=200,
        **{'read.return_value': html_future}
    ))
    aiohttp.get.return_value = resp_future
    movie = Movie('foo', None)
    assert await movie.get_plot() == 'Hello'
    aiohttp.get.assert_called_once_with(
        'http://akas.imdb.com/title/foo/plotsummary',
    )


@mock.patch('halliwell.parser.movie.aiohttp')
@pytest.mark.asyncio
async def test_find_plot_no_data(aiohttp):
    html = "<body></body>"
    html_future = asyncio.Future()
    html_future.set_result(html)
    resp_future = asyncio.Future()
    resp_future.set_result(mock.MagicMock(
        status=200,
        **{'read.return_value': html_future}
    ))
    aiohttp.get.return_value = resp_future
    movie = Movie('foo', None)
    assert await movie.get_plot() is None
    aiohttp.get.assert_called_once_with(
        'http://akas.imdb.com/title/foo/plotsummary',
    )


@mock.patch('halliwell.parser.movie.aiohttp')
@pytest.mark.asyncio
async def test_find_plot_no_response(aiohttp):
    resp_future = asyncio.Future()
    resp_future.set_result(mock.MagicMock(
        status=404,
    ))
    aiohttp.get.return_value = resp_future
    movie = Movie('foo', None)
    assert await movie.get_plot() is None
    aiohttp.get.assert_called_once_with(
        'http://akas.imdb.com/title/foo/plotsummary',
    )


@mock.patch('halliwell.parser.movie.aiohttp')
@pytest.mark.asyncio
async def test_update_no_plot(aiohttp):
    resp_future = asyncio.Future()
    resp_future.set_result(mock.MagicMock(
        status=404,
    ))
    aiohttp.get.return_value = resp_future
    movie = Movie('foo', None)
    movie.cast = set()
    assert await movie.update() is None
    assert 'no plot summary found' in movie.plot
    aiohttp.get.assert_called_once_with(
        'http://akas.imdb.com/title/foo/plotsummary',
    )


@mock.patch('halliwell.parser.movie.aiohttp')
@pytest.mark.asyncio
async def test_update_plot(aiohttp):
    html = dedent("""
    <body>
        <div id="plotSynopsis">Hello</div>
    </body>
    """)
    html_future = asyncio.Future()
    html_future.set_result(html)
    resp_future = asyncio.Future()
    resp_future.set_result(mock.MagicMock(
        status=200,
        **{'read.return_value': html_future}
    ))
    aiohttp.get.return_value = resp_future
    movie = Movie('foo', None)
    movie.cast = set()
    assert await movie.update() is None
    assert movie.plot == 'Hello'
    aiohttp.get.assert_called_once_with(
        'http://akas.imdb.com/title/foo/plotsummary',
    )


@mock.patch('halliwell.parser.movie.aiohttp')
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
    html_future = asyncio.Future()
    html_future.set_result(html)
    resp_future = asyncio.Future()
    resp_future.set_result(mock.MagicMock(
        status=200,
        **{'read.return_value': html_future}
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


@mock.patch('halliwell.parser.movie.aiohttp')
@pytest.mark.asyncio
async def test_find_cast_no_response(aiohttp):
    resp_future = asyncio.Future()
    resp_future.set_result(mock.MagicMock(
        status=404,
    ))
    aiohttp.get.return_value = resp_future
    movie = Movie('foo', None)
    assert await movie.get_cast() == set()
    aiohttp.get.assert_called_once_with(
        'http://akas.imdb.com/title/foo/combined',
    )


@mock.patch('halliwell.parser.movie.aiohttp')
@pytest.mark.asyncio
async def test_update_cast(aiohttp):
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
    html_future = asyncio.Future()
    html_future.set_result(html)
    resp_future = asyncio.Future()
    resp_future.set_result(mock.MagicMock(
        status=200,
        **{'read.return_value': html_future}
    ))
    aiohttp.get.return_value = resp_future
    movie = Movie('foo', None)
    movie.plot = ''
    await movie.update()
    assert len(movie.cast) == 2
    assert Person('nm0123456', None) in movie.cast
    assert Person('nm1234567', None) in movie.cast
    aiohttp.get.assert_called_once_with(
        'http://akas.imdb.com/title/foo/combined',
    )
