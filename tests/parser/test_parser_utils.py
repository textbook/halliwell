from asynctest import mock
import pytest

from halliwell.parser.utils import get_page_content

from helpers import future_from


@pytest.mark.parametrize('status,expected', [
    (200, 'hello world'),
    (404, None),
])
@mock.patch('halliwell.parser.utils.aiohttp')
@pytest.mark.asyncio
async def test_get_page_content(aiohttp, status, expected):
    aiohttp.get.return_value = future_from(mock.MagicMock(
        status=status,
        **{'read.return_value': future_from('hello world')},
    ))
    assert await get_page_content('url') == expected
    aiohttp.get.assert_called_once_with('url')
