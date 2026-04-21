from __future__ import annotations

import tdir

from fmix import audio_file


def test_read_write():
    data, samplerate = audio_file.read('test/audio/one.m4a')
    assert samplerate == 48000
    assert data.shape == (303104, 1)

    with tdir():
        audio_file.write('out.m4a', data, samplerate)
        d, s = audio_file.read('out.m4a')
        assert s == samplerate
        assert d.shape == data.shape
