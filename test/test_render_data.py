from pathlib import Path

from numpy import testing
from pytest import mark

from fmix import audio_file
from fmix.fmix import render_samples

from .invocation import REWRITE_TEST_DATA, make_fmix

RESULT_FILE = Path('test/audio/result.wav')
ENABLED = False  # This is obsolete anyway


@mark.parametrize('mixfile', ['short'])
def test_render_data(mixfile):
    fmix = make_fmix(mixfile)
    actual = render_samples(fmix)

    if RESULT_FILE.exists() and not REWRITE_TEST_DATA:
        expected, _ = audio_file.read(RESULT_FILE)
        if ENABLED:
            testing.assert_allclose(actual, expected)
    else:
        audio_file.write(RESULT_FILE, actual, fmix.rate)
