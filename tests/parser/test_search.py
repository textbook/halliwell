import asyncio
from textwrap import dedent

from asynctest import mock
import pytest

from halliwell.parser import movie_finder


@pytest.mark.parametrize('args,results', [
    ((), 3),
    ((2,), 2),
    ((201,), ValueError),
])
@mock.patch('halliwell.parser.search.aiohttp')
@pytest.mark.asyncio
async def test_find(aiohttp, args, results):
    html = dedent("""
    <body>
        <table class="findList"><tbody>
            <tr><a href="/title/tt0123456">Foo</a></tr>
            <tr><a href="/title/tt1234567">Bar</a></tr>
            <tr><a href="/title/tt2345678">Baz</a></tr>
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
    query = 'foo bar'
    if type(results) is type and issubclass(results, Exception):
        with pytest.raises(results):
            await movie_finder.find(query, *args)
    else:
        assert len(await movie_finder.find(query, *args)) == results
        aiohttp.get.assert_called_once_with(
            'http://akas.imdb.com/find?q=foo%20bar&s=tt',
        )


@mock.patch('halliwell.parser.search.aiohttp')
@pytest.mark.asyncio
async def test_find_no_response(aiohttp):
    resp_future = asyncio.Future()
    resp_future.set_result(mock.MagicMock(
        status=404,
    ))
    aiohttp.get.return_value = resp_future
    query = 'foo bar'
    assert await movie_finder.find(query) == []
    aiohttp.get.assert_called_once_with(
        'http://akas.imdb.com/find?q=foo%20bar&s=tt',
    )
