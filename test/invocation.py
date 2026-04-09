from __future__ import annotations

import os
import tomllib
from pathlib import Path

import ffmpeg

from fmix import fmix
from fmix.print_invocation import print_invocation

REWRITE_TEST_DATA = os.environ.get('REWRITE_TEST_DATA')
TEST_DIR = Path(__file__).parent


def run_invocation(name: str):
    with open(TEST_DIR / f'{name}.toml') as fp:
        data = tomllib.loads(fp.read())

    fm = fmix.make_fmix(**data)
    actual = print_invocation(ffmpeg.get_args(fm.render()))
    invocation_file = TEST_DIR / f'{name}.txt'

    if REWRITE_TEST_DATA or not invocation_file.exists():
        with invocation_file.open('w') as fp:
            fp.write(actual)
            expected = actual
    else:
        expected = invocation_file.read_text()

    return data, actual, expected
