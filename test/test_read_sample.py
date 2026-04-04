from __future__ import annotations

import tomllib
from pathlib import Path

import tdir

from fmix import fmix


@tdir('1-2 + 160800.wav', '3-4 + 160800.wav', test=Path('test'))
def test_read_sample():
    with open('test/fmix-sample.toml', 'br') as fp:
        data = tomllib.load(fp)
    fmix.FMix.make(**data)
