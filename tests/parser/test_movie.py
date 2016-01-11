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


@mock.patch('halliwell.parser.models.get_page_content')
@pytest.mark.asyncio
async def test_find_plot_from_synopsis(get_page_content):
    html = dedent("""
    <body>
        <div id="plotSynopsis">Hello</div>
    </body>
    """)
    get_page_content.return_value = future_from(html)
    movie = Movie('foo', None)
    assert await movie.get_plot() == 'Hello'
    get_page_content.assert_called_once_with(
        'http://akas.imdb.com/title/foo/plotsummary',
    )


@mock.patch('halliwell.parser.models.get_page_content')
@pytest.mark.asyncio
async def test_find_plot_from_summaries(get_page_content):
    html = dedent("""
    <body>
        <ul class="zebraList">
            <div class="header">Who cares</div>
            <li class="odd"><p class="plotSummary">Hello</p></li>
            <li class="even"><p class="plotSummary">World</p></li>
        </ul>
    </body>
    """)
    get_page_content.return_value = future_from(html)
    movie = Movie('foo', None)
    assert await movie.get_plot() == 'Hello'
    get_page_content.assert_called_once_with(
        'http://akas.imdb.com/title/foo/plotsummary',
    )


@mock.patch('halliwell.parser.models.get_page_content')
@pytest.mark.asyncio
async def test_find_plot_no_data(get_page_content):
    get_page_content.return_value = future_from('<body></body>')
    movie = Movie('foo', None)
    assert await movie.get_plot() is None
    get_page_content.assert_called_once_with(
        'http://akas.imdb.com/title/foo/plotsummary',
    )


@mock.patch('halliwell.parser.models.get_page_content')
@pytest.mark.asyncio
async def test_find_plot_no_response(get_page_content):
    get_page_content.return_value = future_from(None)
    movie = Movie('foo', None)
    assert await movie.get_plot() is None
    get_page_content.assert_called_once_with(
        'http://akas.imdb.com/title/foo/plotsummary',
    )


@mock.patch('halliwell.parser.models.get_page_content')
@pytest.mark.asyncio
async def test_update_no_plot(get_page_content):
    get_page_content.return_value = future_from('<body></body>')
    movie = Movie('foo', None)
    movie.cast = set()
    assert await movie.update() is None
    assert 'no plot summary found' in movie.plot
    get_page_content.assert_called_once_with(
        'http://akas.imdb.com/title/foo/plotsummary',
    )


@mock.patch('halliwell.parser.models.get_page_content')
@pytest.mark.asyncio
async def test_update_plot(get_page_content):
    html = dedent("""
    <body>
        <div id="plotSynopsis">Hello</div>
    </body>
    """)
    get_page_content.return_value = future_from(html)
    movie = Movie('foo', None)
    movie.cast = set()
    assert await movie.update() is None
    assert movie.plot == 'Hello'
    get_page_content.assert_called_once_with(
        'http://akas.imdb.com/title/foo/plotsummary',
    )


@mock.patch('halliwell.parser.models.get_page_content')
@pytest.mark.asyncio
async def test_find_cast(get_page_content):
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
    get_page_content.return_value = future_from(html)
    movie = Movie('foo', None)
    cast = await movie.get_cast()
    assert len(cast) == 2
    assert Person('nm0123456', None) in cast
    assert Person('nm1234567', None) in cast
    get_page_content.assert_called_once_with(
        'http://akas.imdb.com/title/foo/combined',
    )


@mock.patch('halliwell.parser.models.get_page_content')
@pytest.mark.asyncio
async def test_find_cast_no_cast(get_page_content):
    get_page_content.return_value = future_from('<body></body>')
    movie = Movie('foo', None)
    cast = await movie.get_cast()
    assert len(cast) == 0
    get_page_content.assert_called_once_with(
        'http://akas.imdb.com/title/foo/combined',
    )


@mock.patch('halliwell.parser.models.get_page_content')
@pytest.mark.asyncio
async def test_find_cast_no_response(get_page_content):
    get_page_content.return_value = future_from(None)
    movie = Movie('foo', None)
    assert await movie.get_cast() == set()
    get_page_content.assert_called_once_with(
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
