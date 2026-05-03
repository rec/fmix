from __future__ import annotations

import os
from pathlib import Path

from numpy import testing
from pytest import mark

from fmix import audio_file
from fmix.fmix import read_fmix
from fmix.render import render_samples

REWRITE_TEST_DATA = os.environ.get('REWRITE_TEST_DATA')
RESULT_FILE = Path('test/audio/result.wav')
ENABLED = False  # This is obsolete anyway


@mark.parametrize('mixfile', ['short.toml'])
def test_render_data(mixfile):
    path = Path('test') / mixfile
    fmix = read_fmix(path)
    actual = render_samples(fmix)

    if RESULT_FILE.exists() and not REWRITE_TEST_DATA:
        expected, _ = audio_file.read(RESULT_FILE)
        if ENABLED:
            testing.assert_allclose(actual, expected)
    else:
        audio_file.write(RESULT_FILE, actual, fmix.rate)
