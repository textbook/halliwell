import asyncio
from textwrap import dedent

from asynctest import mock
import pytest

from halliwell.parser.person import Person


def test_init():
    person = Person('foo', 'bar')
    assert person.id_ == 'foo'
    assert person.name == 'bar'
