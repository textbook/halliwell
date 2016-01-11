from textwrap import dedent

from asynctest import mock
import pytest

from halliwell.parser import MOVIE_FINDER, PERSON_FINDER

from helpers import future_from


@pytest.mark.parametrize('args,results', [
    ((), 3),
    ((2,), 2),
    ((201,), ValueError),
])
@mock.patch('halliwell.parser.search.get_page_content')
@pytest.mark.asyncio
async def test_find(get_page_content, args, results):
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
    get_page_content.return_value = future_from(html)
    query = 'foo bar'
    if type(results) is type and issubclass(results, Exception):
        with pytest.raises(results):
            await MOVIE_FINDER.find(query, *args)
    else:
        movies = await MOVIE_FINDER.find(query, *args)
        assert len(movies) == results
        get_page_content.assert_called_once_with(
            'http://akas.imdb.com/find?q=foo%20bar&s=tt&ttype=ft',
        )
        movie = movies[0]
        assert movie.name, movie.id_ == ('Foo', 'tt0123456')


@mock.patch('halliwell.parser.search.get_page_content')
@pytest.mark.asyncio
async def test_find_person(get_page_content):
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
    get_page_content.return_value = future_from(html)
    query = 'foo bar'
    people = await PERSON_FINDER.find(query)
    assert len(people) == 1
    get_page_content.assert_called_once_with(
        'http://akas.imdb.com/find?q=foo%20bar&s=nm',
    )
    person = people[0]
    assert person.name, person.id_ == ('Foo', 'nm0123456')


@mock.patch('halliwell.parser.search.get_page_content')
@pytest.mark.asyncio
async def test_find_no_response(get_page_content):
    get_page_content.return_value = future_from(None)
    query = 'foo bar'
    assert await MOVIE_FINDER.find(query) == []
    get_page_content.assert_called_once_with(
        'http://akas.imdb.com/find?q=foo%20bar&s=tt&ttype=ft',
    )
