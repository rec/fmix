from __future__ import annotations

import os
import tomllib
from pathlib import Path

import ffmpeg
import tdir

from fmix import fmix

REWRITE_TEST_DATA = os.environ.get('REWRITE_TEST_DATA')
FILTERS_FILE = Path('test/filters.txt')
ARG = (
    '-i 9-10 + 160.wav -i 3-4 + 160.wav -i 5-6 + 160.wav -i 7-8 + 160.wav '
    '-filter_complex (filter) -map [s16] MIX + 150.wav'
)


def test_read_sample():
    with open('test/fmix-sample.toml') as fp:
        data = tomllib.loads(fp.read())
    with tdir(
        '1-2 + 160.wav',
        '3-4 + 160.wav',
        '5-6 + 160.wav',
        '7-8 + 160.wav',
        '9-10 + 160.wav',
    ):
        fm = fmix.make_fmix(**data)
    args = ffmpeg.get_args(fm.render())
    (filt,) = (a for a in args if ';' in a)
    arg_str = ' '.join('(filter)' if ';' in a else a for a in args)
    assert ARG == arg_str
    filter_string = '\n'.join((*filt.split(';'), ''))

    if REWRITE_TEST_DATA or not FILTERS_FILE.exists():
        with FILTERS_FILE.open('w') as fp:
            fp.write(filter_string)
    else:
        assert filter_string == FILTERS_FILE.read_text()
