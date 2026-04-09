from __future__ import annotations

import os
from pathlib import Path

import tdir

from .invocation import run_invocation

REWRITE_TEST_DATA = os.environ.get('REWRITE_TEST_DATA')
INVOCATION_FILE = Path('test/sample.txt')
ARG = (
    '-i 9-10 + 160.wav -i 3-4 + 160.wav -i 5-6 + 160.wav -i 7-8 + 160.wav '
    '-filter_complex (filter) -map [s16] MIX + 150.wav'
)


def test_read_sample():
    with tdir(
        '1-2 + 160.wav',
        '3-4 + 160.wav',
        '5-6 + 160.wav',
        '7-8 + 160.wav',
        '9-10 + 160.wav',
    ):
        fm, actual, expected = run_invocation('sample')
        assert actual == expected
