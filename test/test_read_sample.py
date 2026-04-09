from __future__ import annotations

import os
import tomllib
from pathlib import Path

import ffmpeg
import tdir

from fmix import fmix, print_invocation

REWRITE_TEST_DATA = os.environ.get('REWRITE_TEST_DATA')
INVOCATION_FILE = Path('test/invocation.txt')
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
    result = print_invocation.print_invocation(ffmpeg.get_args(fm.render()))

    if REWRITE_TEST_DATA or not INVOCATION_FILE.exists():
        with INVOCATION_FILE.open('w') as fp:
            fp.write(result)
    else:
        assert result == INVOCATION_FILE.read_text()
