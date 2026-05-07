from __future__ import annotations

from . import run_test


def test_help():
    expected, actual = run_test('fmix -h', 'test/help.txt')
    assert expected == actual
