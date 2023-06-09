import pytest
from main import adder


def test_adder():
    assert adder(1, 1) == 2
