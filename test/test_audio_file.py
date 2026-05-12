from __future__ import annotations

import tdir

import fmix
from fmix import audio_file


def test_read_write(monkeypatch):
    data, samplerate = audio_file.read('test/audio/one.m4a')
    assert samplerate == 48000
    length, *rest = data.shape
    assert length == 303104
    assert rest in ([], [1])
    monkeypatch.setattr(fmix, '_samplerate', samplerate)

    with tdir():
        audio_file.write('out.m4a', data)
        d, s = audio_file.read('out.m4a')
        assert s == samplerate
        assert d.shape == data.shape
