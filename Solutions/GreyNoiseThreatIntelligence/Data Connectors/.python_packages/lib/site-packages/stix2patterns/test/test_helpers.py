"""
Test cases for stix2patterns/helpers.py.
"""
import pytest

from stix2patterns.helpers import brackets_check


@pytest.mark.parametrize(
    "value", [
        '[file:size = 1280]',
        ' [file:size = 1280]',
        '( [file:size = 1280])',
        '( ( [file:size = 1280]) )',
        '(( ( ( [file:size = 1280])) ))',
        '[',
    ],
)
def test_brackets_check(value):
    assert brackets_check(value)


@pytest.mark.parametrize(
    "value", [
        None,
        "file:size = 1280",
        "(file:size = 1280)",
        " ( file:size = 1280 ) ",
        " (( (( file:size = 1280 ) )) ) ",
    ]
)
def test_brackets_check_fail(value):
    assert not brackets_check(None)
