from __future__ import annotations

from . import run_test


def test_config_file():
    expected, actual = run_test('fmix -d test/short.toml', 'test/config.toml')
    assert expected == actual
