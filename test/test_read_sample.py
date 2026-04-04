from __future__ import annotations

import tomllib


def test_read_sample():
    with open('test/fmix-sample.toml', 'br') as fp:
        data = tomllib.load(fp)
        assert data
