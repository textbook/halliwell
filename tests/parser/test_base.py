import asyncio
from textwrap import dedent

from asynctest import mock
import pytest

from halliwell.parser.models import IMDbBase


class TestImplementation(IMDbBase):

    FRIENDLY_URL = 'ID: {id_}'

    def _data(self):
        return 'baz'

    async def update(self):
        pass  # pragma: no cover


def test_init():
    data = dict(id_='foo', name='bar')
    inst = TestImplementation(**data)
    for attr, val in data.items():
        assert getattr(inst, attr) == val


def test_str():
    inst = TestImplementation('foo', 'bar')
    assert str(inst) == dedent("""
    *bar*

    baz

    For more information see: ID: foo
    """).strip()


@pytest.mark.parametrize('first,second,expected', [
    (TestImplementation('foo', 'bar'), TestImplementation('foo', 'baz'), True),
    (TestImplementation('foo', 'bar'), TestImplementation('bar', 'bar'), False),
    (TestImplementation('foo', 'bar'), object(), False),
])
def test_eq(first, second, expected):
    if expected:
        assert first == second
    else:
        assert first != second


@pytest.mark.parametrize('first,second,expected', [
    (TestImplementation('foo', 'bar'), TestImplementation('foo', 'baz'), True),
    (TestImplementation('foo', 'bar'), TestImplementation('bar', 'bar'), False),
])
def test_hash(first, second, expected):
    if expected:
        assert hash(first) == hash(second)
    else:
        assert hash(first) != hash(second)


@mock.patch('halliwell.parser.models.aiohttp')
@pytest.mark.asyncio
async def test_from_id_success(aiohttp):
    html = '<h1><span itemprop="name">Foo</span></h1>'
    html_future = asyncio.Future()
    html_future.set_result(html)
    resp_future = asyncio.Future()
    resp_future.set_result(mock.MagicMock(
        status=200,
        **{'read.return_value': html_future}
    ))
    aiohttp.get.return_value = resp_future
    inst = await TestImplementation.from_id('foo', 'bar')
    assert inst.id_ == 'bar'
    assert inst.name == 'Foo'
    aiohttp.get.assert_called_once_with('http://akas.imdb.com/foo/bar')


@mock.patch('halliwell.parser.models.aiohttp')
@pytest.mark.asyncio
async def test_from_id_failure(aiohttp):
    resp_future = asyncio.Future()
    resp_future.set_result(mock.MagicMock(
        status=404,
    ))
    aiohttp.get.return_value = resp_future
    with pytest.raises(ValueError):
        await TestImplementation.from_id('foo', 'bar')
    aiohttp.get.assert_called_once_with('http://akas.imdb.com/foo/bar')
