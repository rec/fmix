from __future__ import annotations

import os
import tempfile
import tomllib
from pathlib import Path

import ffmpeg

from fmix import fmix

REWRITE_TEST_DATA = os.environ.get('REWRITE_TEST_DATA')
FILTERS_FILE = Path('test/filters.txt')
MIX_FILE = Path('test/audio/mix.m4a')
ARG = (
    '-i "9-10 + 160.wav" -i "3-4 + 160.wav" -i "5-6 + 160.wav" -i "7-8 + 160.wav" '
    '-filter_complex (filter) -map [s16] MIX'
)


def test_read_sample():
    with open('test/fmix-sample.toml') as fp:
        data = tomllib.loads(fp.read())

    with tempfile.NamedTemporaryFile() as tfile:
        if write_mix := not REWRITE_TEST_DATA and MIX_FILE.exists():
            data['files']['output_file'] = tfile.name
            del data['files']['output_root']

        fm = fmix.make_fmix(**data)
        render = fm.render()
        args = ffmpeg.get_args(render)
        (filt,) = (a for a in args if ';' in a)
        arg_str = ' '.join('(filter)' if ';' in a else a for a in args)
        assert ARG == arg_str
        filter_string = '\n'.join((*filt.split(';'), ''))

        if REWRITE_TEST_DATA or not FILTERS_FILE.exists():
            with FILTERS_FILE.open('w') as fp:
                fp.write(filter_string)
        else:
            assert filter_string == FILTERS_FILE.read_text()

        render.run()
        if write_mix:
            actual = Path(tfile.name).read_bytes()
            expected = MIX_FILE.read_bytes()
            assert actual == expected
