from __future__ import annotations

import os
import tomllib
from pathlib import Path
from typing import Any

import ffmpeg

from fmix import fmix
from fmix.print_invocation import print_invocation

REWRITE_TEST_DATA = os.environ.get('REWRITE_TEST_DATA')
TEST_DIR = Path(__file__).parent


def make_fmix(name: str) -> fmix.FMix:
    return _make_fmix(name)[0]


def _make_fmix(name: str) -> tuple[fmix.FMix, dict[str, Any]]:
    with open(TEST_DIR / f'{name}.toml') as fp:
        data = tomllib.loads(fp.read())

    return fmix.make_fmix(**data), data


def run_invocation(name: str):
    fm, data = _make_fmix(name)
    actual = print_invocation(ffmpeg.get_args(fm.render()))
    invocation_file = TEST_DIR / f'{name}.txt'

    if REWRITE_TEST_DATA or not invocation_file.exists():
        with invocation_file.open('w') as fp:
            fp.write(actual)
            expected = actual
    else:
        expected = invocation_file.read_text()

    return data, actual, expected
