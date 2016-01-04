import pytest

from halliwell.utils import extract_quoted_text, friendly_list


@pytest.mark.parametrize('input_,expected', [
    ([], ''),
    (['foo'], 'foo'),
    (['foo', 'bar'], 'foo and bar'),
    (['foo', 'bar', 'baz'], 'foo, bar and baz'),
    (['foo', 'bar', 'baz', 'etc'], 'foo, bar, baz and etc'),
])
def test_friendly_list(input_, expected):
    assert friendly_list(input_) == expected


@pytest.mark.parametrize('input_,expected', [
    ('actor in "crank" and "napoleon dynamite"',
     ['crank', 'napoleon dynamite']),
])
def test_extract_quoted_text(input_, expected):
    assert extract_quoted_text(input_) == expected
