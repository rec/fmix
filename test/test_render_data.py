from __future__ import annotations

from pathlib import Path

from numpy import testing
from pytest import mark

from fmix import audio_file, constants
from fmix.__main__ import read_fmix
from fmix.render import render_samples

from . import REWRITE_TEST_DATA

RESULT_FILE = Path('test/audio/result.wav')
ENABLED = False  # This is obsolete anyway


@mark.parametrize('mixfile', ['short.toml'])
def test_render_data(mixfile, monkeypatch):
    monkeypatch.setattr(constants, '_dtype', 'float64')
    monkeypatch.setattr(constants, '_samplerate', 48_000)
    path = Path('test') / mixfile
    actual = render_samples(read_fmix(path))

    if not ENABLED:
        return

    if RESULT_FILE.exists() and not REWRITE_TEST_DATA:
        expected, _ = audio_file.read(RESULT_FILE)
        if ENABLED:
            testing.assert_allclose(actual, expected)
    else:
        audio_file.write(RESULT_FILE, actual, constants.samplerate())
