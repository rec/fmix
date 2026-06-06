from __future__ import annotations

import subprocess as sp
from pathlib import Path

import tdir
from numpy import testing
from pytest import mark

from fmix import audio_file, constants
from fmix.fmix import FMix
from fmix.read_tyro import read_file
from fmix.render import render_samples

from . import REWRITE_TEST_DATA

RESULT_FILE = Path('test/audio/short.wav')


@mark.parametrize('mixfile', ['short.toml'])
def test_render_data(mixfile, monkeypatch):
    monkeypatch.setattr(constants, '_dtype', 'float64')
    monkeypatch.setattr(constants, '_samplerate', 48_000)
    path = Path('test') / mixfile
    actual = render_samples(FMix(**read_file(path)))

    if RESULT_FILE.exists() and not REWRITE_TEST_DATA:
        expected, _ = audio_file.read(RESULT_FILE)
        testing.assert_allclose(actual, expected)
    else:
        audio_file.write(RESULT_FILE, actual, constants.samplerate())


@mark.parametrize('mixfile', ['test/short.toml'])
def test_regression(mixfile):
    if REWRITE_TEST_DATA or not RESULT_FILE.exists():
        cmd = 'fmix', mixfile, '-o', str(RESULT_FILE)
        out = sp.run(cmd, text=True, capture_output=True)
        assert out.stderr == ''
    else:
        with tdir(chdir=False) as outdir:
            outfile = f'{outdir}/out.wav'
            cmd = 'fmix', mixfile, '-o', outfile
            out = sp.run(cmd, text=True, capture_output=True)
            assert out.stderr == ''
            actual, _ = audio_file.read(outfile)
        expected, _ = audio_file.read(RESULT_FILE)
        testing.assert_allclose(actual, expected)
