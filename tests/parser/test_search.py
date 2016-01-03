import asyncio
from textwrap import dedent

from asynctest import mock
import pytest

from halliwell.parser import movie_finder, person_finder


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
            <tr>
                <td></td>
                <td class="result_text"><a href="/title/tt0123456">Foo</a></td>
            </tr>
            <tr>
                <td></td>
                <td class="result_text"><a href="/title/tt1234567">Bar</a></td>
            </tr>
            <tr>
                <td></td>
                <td class="result_text"><a href="/title/tt2345678">Baz</a></td>
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
    query = 'foo bar'
    if type(results) is type and issubclass(results, Exception):
        with pytest.raises(results):
            await movie_finder.find(query, *args)
    else:
        movies = await movie_finder.find(query, *args)
        assert len(movies) == results
        aiohttp.get.assert_called_once_with(
            'http://akas.imdb.com/find?q=foo%20bar&s=tt&ttype=ft',
        )
        movie = movies[0]
        assert movie.name, movie.id_ == ('Foo', 'tt0123456')


@mock.patch('halliwell.parser.search.aiohttp')
@pytest.mark.asyncio
async def test_find_person(aiohttp):
    html = dedent("""
    <body>
        <table class="findList"><tbody>
            <tr>
                <td></td>
                <td class="result_text"><a href="/name/nm0123456">Foo</a></td>
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
    query = 'foo bar'
    people = await person_finder.find(query)
    assert len(people) == 1
    aiohttp.get.assert_called_once_with(
        'http://akas.imdb.com/find?q=foo%20bar&s=nm',
    )
    person = people[0]
    assert person.name, person.id_ == ('Foo', 'nm0123456')


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
        'http://akas.imdb.com/find?q=foo%20bar&s=tt&ttype=ft',
    )
