from textwrap import dedent

from asynctest import mock
import pytest

from halliwell.parser import Movie, Person

from helpers import future_from


def test_init():
    person = Person('foo', 'bar')
    assert person.id_ == 'foo'
    assert person.name == 'bar'
    assert person.bio is None
    assert person.filmography is None
    assert person.url == 'http://www.imdb.com/name/foo/'


def test_str():
    person = Person('foo', 'bar')
    assert str(person).startswith('*bar*')
    assert str(person).endswith(
        'For more information see: http://www.imdb.com/name/foo/',
    )


@mock.patch('halliwell.parser.models.aiohttp')
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
    resp_future = future_from(mock.MagicMock(
        status=200,
        **{'read.return_value': future_from(html)}
    ))
    aiohttp.get.return_value = resp_future
    person = Person('foo', None)
    assert await person.get_bio() == 'The bio'
    aiohttp.get.assert_called_once_with('http://akas.imdb.com/name/foo/bio')


@mock.patch('halliwell.parser.models.aiohttp')
@pytest.mark.asyncio
async def test_update_no_bio(aiohttp):
    resp_future = future_from(mock.MagicMock(status=404))
    aiohttp.get.return_value = resp_future
    person = Person('foo', None)
    person.filmography = {}
    assert await person.update() is None
    assert 'no biographical information found' in person.bio
    aiohttp.get.assert_called_once_with('http://akas.imdb.com/name/foo/bio')


@mock.patch.object(Person, 'get_bio')
@pytest.mark.asyncio
async def test_update_bio(get_plot):
    get_plot.return_value = future_from('The bio')
    person = Person('foo', None)
    person.filmography = {}
    assert await person.update() is None
    assert person.bio == 'The bio'
    get_plot.assert_called_once_with()


@mock.patch.object(Person, 'get_bio')
@pytest.mark.asyncio
async def test_update_bio_exists(get_plot):
    get_plot.return_value = future_from('The bio')
    person = Person('foo', None)
    person.filmography = {}
    person.bio = ''
    assert await person.update() is None
    get_plot.assert_not_called()


@mock.patch('halliwell.parser.models.aiohttp')
@pytest.mark.asyncio
async def test_get_filmography_success(aiohttp):
    html = dedent("""
    <div id="filmography">
        <div class="head" data-category="actor"></div>
        <div class="filmo-category-section">
            <div id="actor-tt0123456"><b>
                <a href="/title/tt0123456">Foo</a>
            </b></div>
            <div id="actor-tt1234567"><b>
                <a href="/title/tt1234567">Bar</a>
            </b></div>
        </div>
        <div class="head" data-category="director"></div>
        <div class="filmo-category-section">
            <div id="director-tt2345678"><b>
                <a href="/title/tt2345678">Baz</a>
            </b></div>
        </div>
    </div>
    """)
    resp_future = future_from(mock.MagicMock(
        status=200,
        **{'read.return_value': future_from(html)}
    ))
    aiohttp.get.return_value = resp_future
    person = Person('foo', None)
    filmography = await person.get_filmography()
    assert Movie('tt0123456', None) in filmography['actor']
    assert Movie('tt1234567', None) in filmography['actor']
    assert Movie('tt2345678', None) in filmography['director']
    aiohttp.get.assert_called_once_with(
        'http://akas.imdb.com/name/foo/maindetails',
    )


@mock.patch('halliwell.parser.models.aiohttp')
@pytest.mark.asyncio
async def test_get_filmography_failure(aiohttp):
    resp_future = future_from(mock.MagicMock(status=404))
    aiohttp.get.return_value = resp_future
    person = Person('foo', None)
    filmography = await person.get_filmography()
    assert filmography == {}
    aiohttp.get.assert_called_once_with(
        'http://akas.imdb.com/name/foo/maindetails',
    )


@mock.patch.object(Person, 'get_filmography')
@pytest.mark.asyncio
async def test_update_filmography(get_filmography):
    get_filmography.return_value = future_from({})
    person = Person('foo', None)
    person.bio = ''
    assert await person.update() is None
    assert person.filmography == {}
    get_filmography.assert_called_once_with()


@mock.patch.object(Person, 'get_filmography')
@pytest.mark.asyncio
async def test_update_filmography_exists(get_filmography):
    get_filmography.return_value = future_from({})
    person = Person('foo', None)
    person.bio = ''
    person.filmography = {}
    assert await person.update() is None
    get_filmography.assert_not_called()
