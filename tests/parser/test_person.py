import asyncio
from textwrap import dedent

from asynctest import mock
import pytest

from halliwell.parser.person import Person


def test_init():
    person = Person('foo', 'bar')
    assert person.id_ == 'foo'
    assert person.name == 'bar'
    assert person.bio is None
    assert person.url == 'http://www.imdb.com/name/foo/'


def test_str():
    person = Person('foo', 'bar')
    assert str(person).startswith('*bar*')
    assert str(person).endswith(
        'For more information see: http://www.imdb.com/name/foo/',
    )


@mock.patch('halliwell.parser.person.aiohttp')
@pytest.mark.asyncio
async def test_find_plot_from_synopsis(aiohttp):
    html = dedent("""
    <body>
        <a name="mini_bio"></a>
        <h4 class="li_group"></h4>
        <div class="soda_odd">
            <p>The bio</p>
            <p>Its author</p>
        </div>
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
    person = Person('foo', None)
    assert await person.get_bio() == 'The bio'
    aiohttp.get.assert_called_once_with('http://akas.imdb.com/name/foo/bio')


@mock.patch('halliwell.parser.person.aiohttp')
@pytest.mark.asyncio
async def test_update_no_plot(aiohttp):
    resp_future = asyncio.Future()
    resp_future.set_result(mock.MagicMock(
        status=404,
    ))
    aiohttp.get.return_value = resp_future
    person = Person('foo', None)
    assert await person.update() is None
    assert 'no biographical information found' in person.bio
    aiohttp.get.assert_called_once_with('http://akas.imdb.com/name/foo/bio')


@mock.patch('halliwell.parser.person.aiohttp')
@pytest.mark.asyncio
async def test_update_plot(aiohttp):
    html = dedent("""
    <body>
        <a name="mini_bio"></a>
        <h4 class="li_group"></h4>
        <div class="soda_odd">
            <p>The bio</p>
            <p>Its author</p>
        </div>
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
    person = Person('foo', None)
    assert await person.update() is None
    assert person.bio == 'The bio'
    aiohttp.get.assert_called_once_with('http://akas.imdb.com/name/foo/bio')
